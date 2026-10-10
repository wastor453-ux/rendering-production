#!/bin/bash
# R-008: Install OS packages via pinned Ubuntu snapshot. Fail closed.
#
# Usage: install_snapshot.sh <package> [<package> ...]
#
# - Configures snapshot.ubuntu.com sources from $UBUNTU_SNAPSHOT (required).
# - Fails closed if UBUNTU_SNAPSHOT is empty, snapshot setup fails, or a
#   rolling (non-snapshot) source is detected after configuration.
# - Logs: snapshot timestamp, active apt sources, resolved package versions.
#
# This script is the ONLY permitted apt-install path in the workflow.
# Direct `apt-get install` calls bypass R-008 and must not exist.
set -euo pipefail

if [ $# -eq 0 ]; then
  echo "FATAL R-008: no packages specified" >&2
  exit 1
fi

if [ -z "${UBUNTU_SNAPSHOT:-}" ]; then
  echo "FATAL R-008: UBUNTU_SNAPSHOT is not set — refusing rolling install" >&2
  exit 1
fi

echo "R-008: snapshot timestamp = $UBUNTU_SNAPSHOT"
SNAP_URL="https://snapshot.ubuntu.com/ubuntu/${UBUNTU_SNAPSHOT}"

# Backup original sources (best effort)
sudo cp /etc/apt/sources.list.d/ubuntu.sources /tmp/ubuntu.sources.bak 2>/dev/null || true

# Configure snapshot source (noble + noble-updates, main only)
sudo tee /etc/apt/sources.list.d/ubuntu-snapshot.sources > /dev/null <<EOF
Types: deb
URIs: $SNAP_URL
Suites: noble noble-updates
Components: main
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF

# Disable the rolling sources so nothing resolves outside the snapshot
sudo rm -f /etc/apt/sources.list.d/ubuntu.sources

echo "R-008: active apt sources:"
grep -h "^URIs:" /etc/apt/sources.list.d/*.sources 2>/dev/null || echo "(none)"

# Fail closed: every configured source must be the snapshot URL
if grep -rh "^URIs:" /etc/apt/sources.list.d/*.sources 2>/dev/null | grep -qv "$SNAP_URL"; then
  echo "FATAL R-008: non-snapshot (rolling) apt source detected — refusing install" >&2
  exit 1
fi

echo "R-008: updating package lists from snapshot..."
if ! sudo apt-get update -qq 2>/tmp/apt-snapshot.err; then
  echo "FATAL R-008: snapshot apt-get update failed:" >&2
  cat /tmp/apt-snapshot.err >&2
  exit 1
fi

echo "R-008: installing: $*"
sudo apt-get install -y -qq --no-install-recommends "$@"

echo "R-008: resolved versions:"
for pkg in "$@"; do
  VER=$(dpkg-query -W -f='${Version}' "$pkg" 2>/dev/null || echo "NOT-INSTALLED")
  echo "  $pkg = $VER"
  if [ "$VER" = "NOT-INSTALLED" ]; then
    echo "FATAL R-008: package $pkg failed to install" >&2
    exit 1
  fi
done
echo "R-008: install complete from snapshot $UBUNTU_SNAPSHOT"
