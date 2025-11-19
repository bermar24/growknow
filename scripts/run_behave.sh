#!/usr/bin/env bash
# Run behave with Django settings and project PYTHONPATH set.
# Usage: ./scripts/run_behave.sh [behave-args]
set -euo pipefail

# Ensure we run from the repository root
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Export needed environment variables so Django can be imported by step modules
export PYTHONPATH="$REPO_ROOT"
export DJANGO_SETTINGS_MODULE=backend.settings

# Forward any arguments to behave
if ! command -v behave >/dev/null 2>&1; then
  echo "behave not found in PATH. Install behave (pip install behave) or run using your project's venv."
  exit 2
fi

exec behave "$@"

