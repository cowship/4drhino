#!/usr/bin/env bash
# Linux dev environment setup: creates .venv and installs pytest.
# Usage: bash scripts/setup_dev.sh   (run from anywhere)
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
    # ensurepip may be missing on Debian/Ubuntu without python3-venv
    if ! python3 -m venv .venv >/dev/null 2>&1; then
        rm -rf .venv
        python3 -m venv --without-pip .venv
    fi
fi

if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
    tmp="$(mktemp -d)"
    curl -sSL https://bootstrap.pypa.io/get-pip.py -o "$tmp/get-pip.py"
    .venv/bin/python "$tmp/get-pip.py" -q
    rm -rf "$tmp"
fi

.venv/bin/python -m pip install -q --upgrade pytest

echo "Done. Run tests with: .venv/bin/python -m pytest"
