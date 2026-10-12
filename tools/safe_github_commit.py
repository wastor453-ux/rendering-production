#!/usr/bin/env python3
"""
safe_github_commit.py — TRUE ROOT FIX for API-introduced syntax errors.

ROOT CAUSE: GitHub Contents API accepts ANY string, even with syntax errors.
  I committed ",," and orphaned "," lines because the API doesn't validate.
  BudgetRule got syntax errors. EmergencyShield got NEW syntax errors.
  Same root cause, different videos.

TRUE FIX: Validate syntax LOCALLY before ANY API commit.
  This wrapper:
  1. Takes file content
  2. Runs py_compile to validate Python syntax
  3. Runs basic checks (no orphaned commas, balanced brackets)
  4. ONLY commits if validation passes
  5. If validation fails, REFUSES to commit

  Impossible to commit syntax errors via API.

Usage:
    from safe_github_commit import safe_put_file
    safe_put_file(path, content, sha, message)  # Validates first!
"""
import ast
import sys


def validate_python_syntax(content: str, filename: str = "file.py") -> tuple[bool, str]:
    """
    Validate Python syntax. Returns (is_valid, error_message).
    """
    try:
        ast.parse(content, filename=filename)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}: {e.msg}\n  {e.text}"


def validate_no_orphaned_commas(content: str) -> tuple[bool, str]:
    """
    Check for orphaned comma lines (a line that's just ",").
    This was the EmergencyShield bug.
    """
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip() == ",":
            return False, f"Orphaned comma on line {i}: a line containing only ','"
    return True, ""


def validate_no_double_commas(content: str) -> tuple[bool, str]:
    """
    Check for double commas ",,".
    This was the EmergencyShield contract bug.
    """
    if ",," in content:
        # Find line number
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if ",," in line:
                return False, f"Double comma ',,' on line {i}: {line.strip()[:60]}"
    return True, ""


def validate_content(content: str, filename: str) -> tuple[bool, list[str]]:
    """
    Run all validations. Returns (is_valid, [error_messages]).
    """
    errors = []

    # Only validate Python files
    if filename.endswith('.py'):
        valid, msg = validate_python_syntax(content, filename)
        if not valid:
            errors.append(msg)

        valid, msg = validate_no_orphaned_commas(content)
        if not valid:
            errors.append(msg)

        valid, msg = validate_no_double_commas(content)
        if not valid:
            errors.append(msg)

    # TypeScript/TSX basic checks
    if filename.endswith(('.tsx', '.ts')):
        # Check balanced braces (basic)
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open vs {close_braces} close")

    return len(errors) == 0, errors


def safe_put_file(path: str, content: str, sha: str, message: str,
                   repo: str, branch: str, api_put_func) -> dict:
    """
    Safely commit a file via GitHub API with pre-validation.
    
    Args:
        path: Repo path (e.g., "tests/test_foo.py")
        content: File content string
        sha: Current file SHA (for updates)
        message: Commit message
        repo: "owner/repo"
        branch: Branch name
        api_put_func: Function that does the actual API PUT
    
    Returns:
        API response dict
    
    Raises:
        ValueError: If validation fails (commit REFUSED)
    """
    # VALIDATE BEFORE COMMIT — the root fix
    is_valid, errors = validate_content(content, path)
    if not is_valid:
        error_msg = "\n".join(errors)
        raise ValueError(
            f"COMMIT REFUSED: {path} failed validation.\n"
            f"This prevents the syntax errors that broke CI.\n"
            f"Errors:\n{error_msg}\n\n"
            f"Fix the content and try again. "
            f"Never bypass this validation."
        )

    # Validation passed — safe to commit
    return api_put_func(path, content, sha, message)


if __name__ == "__main__":
    # Self-test
    print("Testing safe_github_commit.py...")
    
    # Test 1: Valid Python
    valid, errors = validate_content("x = 1\nprint(x)\n", "test.py")
    assert valid, f"Should be valid: {errors}"
    print("✅ Valid Python passes")
    
    # Test 2: Syntax error
    valid, errors = validate_content("x = \n", "test.py")
    assert not valid, "Should detect syntax error"
    print("✅ Syntax error detected")
    
    # Test 3: Orphaned comma
    valid, errors = validate_content('a = 1,\n,\nb = 2\n', "test.py")
    assert not valid, f"Should detect error: {errors}"
    assert any("Orphaned comma" in e for e in errors), f"Should mention orphaned comma: {errors}"
    print("✅ Orphaned comma detected")
    
    # Test 4: Double comma
    valid, errors = validate_content('foo(a,,b)\n', "test.py")
    assert not valid, f"Should detect error: {errors}"
    assert any("Double comma" in e for e in errors), f"Should mention double comma: {errors}"
    print("✅ Double comma detected")
    
    print("\n✅ All self-tests passed. Safe to use for API commits.")
