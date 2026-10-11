#!/usr/bin/env python3
"""pipeline_check.py — fail-closed stage-gate engine + Astor Legacy stage table.

Generic engine (project-independent): a stage may run only if every required
input exists, is valid, belongs to the same run_id, and every gate passes.
Any failure -> (False, reasons); the downstream stage must not run.

Two APIs:
  Library: check_stage(stage_name, ctx), verify_outputs(stage_name, ctx),
           gate_stage(stage_name, run_id, registry_path)  # exits 2 on fail
           register_artifact(registry_path, run_id, key, path, kind="auto")
  CLI:     pipeline_check.py --stage S9_assembly --registry reg.json --run-id ID
           pipeline_check.py --register KEY=PATH --registry reg.json --run-id ID
           pipeline_check.py --verify-outputs S6_planning --registry reg.json --run-id ID
           Exit codes: 0 = pass, 1 = usage/error, 2 = gate failure.

Project adapter: STAGES / OUTPUTS tables below define the 12 production
stages. Other projects supply their own tables; the engine does not change.

Stage contracts were resolved against the real executors (2026-10-11):
execution order is S7_render -> S9_assembly -> S8_sound -> S10_qa
(the workflow assembles video before the SFX mix; the earlier S7->S8->S9
order did not match reality). Pre-gates validate UPSTREAM outputs only;
each stage's own outputs are validated by verify_outputs / the next gate.
"""
import argparse
import json
import sys
from pathlib import Path

MEMORY = Path.home() / "memory"
sys.path.insert(0, str(MEMORY / "decisions"))
sys.path.insert(0, str(MEMORY / "issues"))


def _memory_available():
    return (MEMORY / "decisions" / "query.py").exists()


try:
    from validate import check_authorization
except ImportError:  # pragma: no cover - runner without memory system
    check_authorization = None


class GateFail(Exception):
    pass


class RunContext:
    """All state a gate may inspect. Artifacts carry run_id + revision."""
    def __init__(self, run_id, artifacts=None, grants=None, params=None,
                 completions=None):
        self.run_id = run_id
        self.artifacts = artifacts or {}   # key -> dict(run_id, revision, data, ...)
        self.grants = grants or []         # explicit T0 authorizations
        self.params = params or {}         # run-level flags, e.g. {"with_audio": "false"}
        self.completions = completions or {}  # stage -> completion record


# ---- generic validators (project-independent) ----

def v_exists(ctx, key, art):
    if art is None:
        raise GateFail(f"missing required input: {key}")

def v_run_match(ctx, key, art):
    if art is None:
        return  # v_exists records the missing input; fail-closed already
    if art.get("run_id") != ctx.run_id:
        raise GateFail(
            f"run_id mismatch on {key}: got {art.get('run_id')!r}, "
            f"expected {ctx.run_id!r} (mixed-run rejected)")

def v_fresh(ctx, key, art, after_key):
    """Artifact must be at least as new as the input it derives from."""
    other = ctx.artifacts.get(after_key)
    if other and art is not None and art.get("revision", 0) < other.get("revision", 0):
        raise GateFail(f"stale input: {key} (rev {art.get('revision')}) "
                       f"older than {after_key} (rev {other.get('revision')})")

def v_schema(ctx, key, art, schema_fn):
    if art is None:
        return
    ok, why = schema_fn(art.get("data"))
    if not ok:
        raise GateFail(f"schema invalid on {key}: {why}")

def v_decision_approved(ctx, key, art, decision_id):
    """Approved mapping/decision must be live in the ledger (not assumed).

    Degradation: on hosts without the memory system (e.g. CI runners) the
    check is skipped with a warning — it is enforced at dispatch time.
    """
    if not _memory_available():
        print(f"WARN: memory system unavailable; skipping ledger check "
              f"for {decision_id} (enforced at dispatch)", file=sys.stderr)
        return
    import subprocess
    r = subprocess.run(
        [sys.executable, str(MEMORY / "decisions" / "query.py"),
         "--id", decision_id],
        capture_output=True, text=True)
    if "[approved]" not in r.stdout:
        raise GateFail(f"decision {decision_id} not approved in ledger "
                       f"(required by {key})")

def v_authorized(ctx, key, art, action):
    if check_authorization is None:
        raise GateFail(f"authorization system unavailable; cannot allow {action}")
    allowed, tier, reason = check_authorization(action, ctx.grants)
    if not allowed:
        raise GateFail(f"authorization blocked for {action}: {reason} [{tier}]")

def v_audio_input(ctx, key, art):
    # mixed_audio (VO+bed) is required iff the run uses audio.
    # with_audio=false is a supported mode: silent assembly is legitimate.
    if ctx.params.get("with_audio", "true") == "false":
        return
    v_exists(ctx, key, art)


# ---- Astor Legacy stage table (project adapter) ----
# Pre-gates validate UPSTREAM artifacts only. Each stage's own outputs are
# validated by verify_outputs() and by the next stage's pre-gate.

def _beat_schema(data):
    if not isinstance(data, dict) or "beats" not in data:
        return False, "missing 'beats'"
    return True, "ok"

def _ledger_complete(data):
    # Real chunk-ledger format from rendering-production build_ledger.py:
    # {"kind": "chunk-ledger", "expected_chunks", "ok_chunks", "complete", "entries"}
    if not isinstance(data, dict) or data.get("kind") != "chunk-ledger":
        return False, "not a chunk-ledger"
    if not data.get("complete"):
        missing = [e["chunk_id"] for e in data.get("entries", [])
                   if e.get("status") not in ("rendered_ok", "reused_ok")]
        return False, f"incomplete chunks: {missing}"
    return True, "ok"

def _qa_pass(data):
    if not isinstance(data, dict) or data.get("verify_render") != "PASS":
        return False, "verify-render not PASS"
    if not data.get("gate0_editorial"):
        return False, "Gate 0 editorial missing"
    return True, "ok"

def v_visual_modes_approved(ctx, key, artifact):
    """D-002 repo-side enforcement: every beat's visual_mode must be in the
    approved set from visual_mode_schema.json (repository-authoritative).
    Only runs when the `visual_modes_schema` param gives the schema path;
    skipped otherwise (backward compatible). Fail-closed on unknown modes.
    """
    schema_path = ctx.params.get("visual_modes_schema")
    if not schema_path:
        return
    import json as _json
    try:
        with open(schema_path) as f:
            schema = _json.load(f)
    except (OSError, ValueError) as e:
        raise GateFail(f"cannot load visual mode schema {schema_path!r}: {e}")
    approved = {m["id"] for m in schema.get("modes", []) if "id" in m}
    if not approved:
        raise GateFail(f"visual mode schema {schema_path!r} has no modes")
    data = artifact.get("data") or {}
    beats = data.get("beats", []) if isinstance(data, dict) else []
    bad = sorted({b.get("visual_mode") for b in beats
                  if b.get("visual_mode") not in approved})
    if bad:
        raise GateFail(
            f"D-002 violation: unapproved visual modes {bad} "
            f"(not in {schema_path!r})")


def _s11_completions_gate(ctx):
    # Only enforced when the caller opts into strict mode
    # (--require-completions). Direct CLI use without the flag keeps the
    # backward-compatible artifact+auth contract.
    # Key-existence (not truthiness): prevents downgrade via
    # `--define require_completions=` (empty value).
    if "require_completions" in ctx.params:
        v_completions_required(ctx, LOCAL_STAGES)


# Stages with a local sanctioned-runner path whose completion can be
# evidenced in the registry. Workflow stages (S7/S9) are excluded: they run
# on hosted runners with no registry access; their completion is evidenced
# by hosted artifacts validated separately.
LOCAL_STAGES = ["S1_discovery", "S2_selection", "S3_transcript", "S4_script",
                "S5_voice", "S6_planning", "S8_sound", "S10_qa"]

STAGES = {
    # name: ([input defs], [gate defs]); input def = (key, [validators])
    "S1_discovery": (
        [("competitor_list", [v_exists]),
         ("youtube_credential", [v_exists])],
        []),
    "S2_selection": (
        [("ranked_candidates", [v_exists, v_run_match])],
        []),
    "S3_transcript": (
        [("selection", [v_exists, v_run_match])],
        []),
    "S4_script": (
        [("transcript_breakdown", [v_exists, v_run_match])],
        []),
    "S5_voice": (
        [("script", [v_exists, v_run_match]),
         ("voice_lock", [lambda c, k, a: v_decision_approved(c, k, a, "D-001")])],
        []),
    "S6_planning": (
        [("voice_audio", [v_exists, v_run_match])],
        []),
    "S7_render": (
        [("beat_json", [v_exists, v_run_match,
                         lambda c, k, a: v_schema(c, k, a, _beat_schema),
                         lambda c, k, a: v_decision_approved(c, k, a, "D-002"),
                         v_visual_modes_approved])],
        []),
    "S9_assembly": (
        [("chunk_ledger", [v_exists, v_run_match,
                            lambda c, k, a: v_schema(c, k, a, _ledger_complete)]),
         ("mixed_audio", [v_audio_input, v_run_match])],
        []),
    "S8_sound": (
        [("master_video", [v_exists, v_run_match]),
         ("chunk_ledger", [v_exists, v_run_match,
                            lambda c, k, a: v_schema(c, k, a, _ledger_complete)]),
         ("voice_lock_sfx", [lambda c, k, a: v_decision_approved(c, k, a, "D-006")])],
        []),
    "S10_qa": (
        [("final_mix", [v_exists, v_run_match]),
         ("chunk_ledger", [v_exists, v_run_match,
                            lambda c, k, a: v_schema(c, k, a, _ledger_complete)])],
        []),
    "S11_release": (
        [("final_mix", [v_exists, v_run_match]),
         ("qa_report", [v_exists, v_run_match,
                         lambda c, k, a: v_schema(c, k, a, _qa_pass)]),
         ("release_auth", [lambda c, k, a: v_authorized(c, k, a, "release")])],
        [_s11_completions_gate]),
    "S12_post_release": (
        [("platform_asset", [v_exists, v_run_match])],
        []),
}

# Outputs each stage must produce (validated post-execution).
OUTPUTS = {
    "S1_discovery": [("ranked_candidates", [v_exists, v_run_match])],
    "S2_selection": [("selection", [v_exists, v_run_match])],
    "S3_transcript": [("transcript_breakdown", [v_exists, v_run_match])],
    "S4_script": [("script", [v_exists, v_run_match])],
    "S5_voice": [("voice_audio", [v_exists, v_run_match])],
    "S6_planning": [("beat_json", [v_exists, v_run_match,
                                   lambda c, k, a: v_schema(c, k, a, _beat_schema)])],
    "S7_render": [("chunk_ledger", [v_exists, v_run_match,
                                    lambda c, k, a: v_schema(c, k, a, _ledger_complete)])],
    "S9_assembly": [("master_video", [v_exists, v_run_match])],
    "S8_sound": [("final_mix", [v_exists, v_run_match])],
    "S10_qa": [("qa_report", [v_exists, v_run_match,
                              lambda c, k, a: v_schema(c, k, a, _qa_pass)])],
    "S11_release": [("platform_asset", [v_exists, v_run_match])],
    "S12_post_release": [],
}


def check_stage(stage_name, ctx):
    """Fail-closed pre-gate. Returns (ok, reasons)."""
    if stage_name not in STAGES:
        return False, [f"unknown stage: {stage_name}"]
    inputs, gates = STAGES[stage_name]
    reasons = []
    for key, validators in inputs:
        art = ctx.artifacts.get(key)
        for v in validators:
            try:
                v(ctx, key, art)
            except GateFail as e:
                reasons.append(str(e))
    for g in gates:
        try:
            g(ctx)
        except GateFail as e:
            reasons.append(str(e))
    return (len(reasons) == 0), reasons


def verify_outputs(stage_name, ctx):
    """Fail-closed post-gate: the stage produced its declared outputs."""
    if stage_name not in OUTPUTS:
        return False, [f"unknown stage: {stage_name}"]
    reasons = []
    for key, validators in OUTPUTS[stage_name]:
        art = ctx.artifacts.get(key)
        for v in validators:
            try:
                v(ctx, key, art)
            except GateFail as e:
                reasons.append(f"output {key}: {e}")
    return (len(reasons) == 0), reasons


def stage_order():
    # Execution order (S9 video assembly precedes S8 final mix in reality).
    return ["S1_discovery", "S2_selection", "S3_transcript", "S4_script",
            "S5_voice", "S6_planning", "S7_render", "S9_assembly", "S8_sound",
            "S10_qa", "S11_release", "S12_post_release"]


# ---- artifact registry (real files, not fixtures) ----

def _detect_kind(path):
    p = path.lower()
    if p.endswith(".json"):
        return "json"
    if p.endswith((".wav", ".mp3", ".mp4", ".mov", ".mkv")):
        return "media"
    return "text"


def _load_data(path, kind):
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return None
    if kind == "json":
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return None
    if kind == "media":
        return {"exists": True, "bytes": p.stat().st_size}
    try:
        return {"text": p.read_text()[:4000]}
    except OSError:
        return None


def load_registry(registry_path):
    p = Path(registry_path)
    if not p.exists():
        return {"run_id": None, "artifacts": {}}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {"run_id": None, "artifacts": {}}


def save_registry(registry_path, reg):
    p = Path(registry_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(reg, indent=1))


def register_artifact(registry_path, run_id, key, path, kind="auto"):
    """Record a real artifact file into the registry. Returns the entry."""
    kind = _detect_kind(path) if kind == "auto" else kind
    reg = load_registry(registry_path)
    arts = reg.setdefault("artifacts", {})
    prev = arts.get(key, {})
    arts[key] = {"run_id": run_id, "revision": prev.get("revision", 0) + 1,
                 "path": str(path), "kind": kind}
    if not reg.get("run_id"):
        reg["run_id"] = run_id
    save_registry(registry_path, reg)
    return arts[key]


def ctx_from_registry(registry_path, run_id, grants=None):
    reg = load_registry(registry_path)
    artifacts = {}
    for key, meta in reg.get("artifacts", {}).items():
        data = _load_data(meta.get("path", ""), meta.get("kind", "auto"))
        if data is None:
            continue  # file gone/empty/unparseable -> treated as missing
        artifacts[key] = {"run_id": meta.get("run_id"),
                          "revision": meta.get("revision", 1),
                          "data": data, "path": meta.get("path")}
    return RunContext(run_id, artifacts, grants=grants,
                      params=reg.get("params", {}),
                      completions=reg.get("completions", {}))


def set_param(registry_path, run_id, key, value):
    reg = load_registry(registry_path)
    reg.setdefault("params", {})[key] = value
    if not reg.get("run_id"):
        reg["run_id"] = run_id
    save_registry(registry_path, reg)


def record_completion(registry_path, run_id, stage):
    """Record that a stage completed via the sanctioned runner (evidence).

    Binds the record to the stage's declared outputs (from OUTPUTS) so the
    record is evidence of a specific run's artifacts, not a bare claim.
    """
    import time
    reg = load_registry(registry_path)
    comps = reg.setdefault("completions", {})
    outputs = [k for k, _ in OUTPUTS.get(stage, [])]
    comps[stage] = {"run_id": run_id, "ts": int(time.time()),
                    "via": "run_stage", "outputs": outputs}
    save_registry(registry_path, reg)


def v_completions_required(ctx, stages):
    """Prevention (not just detection): required stages must have completion
    records bound to this run. Fails closed on missing or mismatched records.

    Note: covers local stages only. Workflow stages (S7/S9) execute on hosted
    runners with no registry access; their completion is evidenced by hosted
    artifacts (job success, chunk ledger), which the artifact validators
    already check. This validator does not accept records alone as proof of
    substantive correctness — artifact, QA, and authorization gates still apply.
    """
    missing = [s for s in stages
               if ctx.completions.get(s, {}).get("run_id") != ctx.run_id]
    if missing:
        raise GateFail(
            f"missing completion evidence for stages: {', '.join(missing)} "
            f"(run {ctx.run_id}); complete them via the sanctioned runner")


def audit_completions(registry_path, run_id, expected):
    """Detection (not prevention): which expected stages lack completion evidence."""
    reg = load_registry(registry_path)
    comps = reg.get("completions", {})
    missing = [s for s in expected
               if comps.get(s, {}).get("run_id") != run_id]
    return missing


def gate_stage(stage_name, run_id, registry_path, grants=None):
    """Run the pre-gate from a real executor. Exits 2 on failure."""
    ctx = ctx_from_registry(registry_path, run_id, grants)
    ok, reasons = check_stage(stage_name, ctx)
    if not ok:
        print(f"GATE FAIL: {stage_name} blocked:", file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        sys.exit(2)
    print(f"GATE PASS: {stage_name}")
    return ctx


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pipeline stage gate (fail-closed)")
    ap.add_argument("--stage", help="stage id to pre-gate (e.g. S9_assembly)")
    ap.add_argument("--verify-outputs", help="stage id to post-gate")
    ap.add_argument("--register", metavar="KEY=PATH",
                    help="record a real artifact file into the registry")
    ap.add_argument("--kind", default="auto",
                    help="artifact kind for --register (auto|json|media|text)")
    ap.add_argument("--registry", help="artifact registry JSON")
    ap.add_argument("--run-id", help="pipeline run id")
    ap.add_argument("--grant", action="append", default=[],
                    help="explicit T0 authorization (repeatable)")
    ap.add_argument("--define", action="append", default=[], metavar="KEY=VALUE",
                    help="set a run-level param, e.g. with_audio=false (repeatable)")
    ap.add_argument("--require-completions", action="store_true",
                    help="S11 strict mode: require completion evidence for all "
                         "local stages (prevents procedure-stage bypass)")
    ap.add_argument("--record-completion", metavar="STAGE",
                    help="record stage completion evidence (via sanctioned runner)")
    ap.add_argument("--audit-completions", metavar="STAGES",
                    help="comma-separated expected stages; reports those lacking "
                         "completion evidence (detection, not prevention)")
    ap.add_argument("--list-stages", action="store_true")
    args = ap.parse_args(argv)

    if args.list_stages:
        print("\n".join(stage_order()))
        return 0
    if not args.registry or not args.run_id:
        ap.error("--registry and --run-id are required (except with --list-stages)")
    for d in args.define:
        if "=" not in d:
            ap.error(f"--define needs KEY=VALUE, got {d!r}")
        k, v = d.split("=", 1)
        set_param(args.registry, args.run_id, k.strip(), v.strip())
        print(f"param {k.strip()}={v.strip()}")
    did_define = bool(args.define)
    if args.require_completions:
        set_param(args.registry, args.run_id, "require_completions", "1")
        print("param require_completions=1 (S11 strict mode)")
    if args.record_completion:
        record_completion(args.registry, args.run_id, args.record_completion)
        print(f"completion recorded: {args.record_completion}")
        return 0
    if args.audit_completions:
        expected = [s.strip() for s in args.audit_completions.split(",") if s.strip()]
        missing = audit_completions(args.registry, args.run_id, expected)
        if missing:
            print(f"COMPLETION AUDIT: {len(missing)} stage(s) lack evidence: "
                  f"{', '.join(missing)}", file=sys.stderr)
            return 2
        print(f"completion audit clean: {len(expected)} stage(s) evidenced")
        return 0
    if args.register:
        if "=" not in args.register:
            ap.error("--register needs KEY=PATH")
        key, path = args.register.split("=", 1)
        entry = register_artifact(args.registry, args.run_id, key.strip(),
                                  path.strip(), kind=args.kind)
        print(f"registered {key.strip()} -> {path.strip()} "
              f"(rev {entry['revision']})")
        return 0
    if args.stage:
        gate_stage(args.stage, args.run_id, args.registry, args.grant)
        return 0
    if args.verify_outputs:
        ctx = ctx_from_registry(args.registry, args.run_id, args.grant)
        ok, reasons = verify_outputs(args.verify_outputs, ctx)
        if not ok:
            print(f"OUTPUT GATE FAIL: {args.verify_outputs}:", file=sys.stderr)
            for r in reasons:
                print(f"  - {r}", file=sys.stderr)
            return 2
        print(f"OUTPUT GATE PASS: {args.verify_outputs}")
        return 0
    if did_define:
        return 0  # params set; no further command requested
    ap.error("need --stage, --verify-outputs, --register, --define, "
             "--record-completion, --audit-completions, or --list-stages")
    return 1


if __name__ == "__main__":
    sys.exit(main())
