#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  NewsApp — install.sh
#  Entry point for Linux and macOS.
#  Double-click or run:  bash install.sh
# ═══════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "═══════════════════════════════════════════"
echo "  NewsApp Installer"
echo "═══════════════════════════════════════════"

# ── 1. Ensure Python 3.9+ is available ──────────────────────

PYTHON=""
for candidate in python3 python3.12 python3.11 python3.10 python3.9 python; do
    if command -v "$candidate" &>/dev/null; then
        VERSION=$("$candidate" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
        # Accept anything >= (3,9)
        OK=$("$candidate" -c \
            "import sys; print('ok' if sys.version_info >= (3,9) else 'no')" 2>/dev/null)
        if [ "$OK" = "ok" ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo ""
    echo "  Python 3.9+ not found. Attempting to install..."
    OS_TYPE="$(uname -s)"
    if [ "$OS_TYPE" = "Linux" ]; then
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip python3-venv
        PYTHON="python3"
    elif [ "$OS_TYPE" = "Darwin" ]; then
        if command -v brew &>/dev/null; then
            brew install python@3.12
            PYTHON="python3"
        else
            echo ""
            echo "  ✖  Homebrew not found."
            echo "     Install Python from https://python.org then re-run this script."
            exit 1
        fi
    fi
fi

echo "  ✔  Using Python: $($PYTHON --version)"

# ── 2. (Linux only) ensure pip + venv are available ─────────

if [ "$(uname -s)" = "Linux" ]; then
    if ! "$PYTHON" -m pip --version &>/dev/null; then
        sudo apt-get install -y python3-pip
    fi
    if ! "$PYTHON" -m venv --help &>/dev/null; then
        sudo apt-get install -y python3-venv
    fi
fi

# ── 3. Hand off to the Python installer ─────────────────────

echo ""
echo "  Handing off to installer/install.py ..."
echo ""

"$PYTHON" "$SCRIPT_DIR/installer/install.py"
