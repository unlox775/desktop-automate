#!/bin/bash
# cron_run_w_log.sh - Run a Python script with logging
#
# This script executes a Python script using a virtual environment and logs the output.
# It can be configured using environment variables.

# Load secrets file if specified and exists
SECRETS_FILE=${SECRETS_FILE:-"$HOME/.secrets/env.sh"}
if [ -f "$SECRETS_FILE" ]; then
  source "$SECRETS_FILE"
fi

# Set up variables with defaults that can be overridden by environment variables
# Path to Python in virtual environment (default: look for venv in script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON=${VENV_PYTHON:-"$SCRIPT_DIR/venv/bin/python3"}

# Log file location
LOG=${LOG:-"$HOME/cron.log"}

# Log prefix command (optional)
LOG_PREFIX=${LOG_PREFIX:-""}

# Get the script to run and its arguments
SCRIPT="$1"
shift
ARGS="$@"

# Verify Python exists
if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: Python executable not found at $VENV_PYTHON" >&2
  echo "Set VENV_PYTHON environment variable or create a virtual environment at the default location." >&2
  exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT" ]; then
  echo "Error: Script $SCRIPT not found." >&2
  exit 1
fi

# Run the script with logging
if [ -n "$LOG_PREFIX" ] && command -v "$LOG_PREFIX" >/dev/null 2>&1; then
  $VENV_PYTHON "$SCRIPT" $ARGS 2>&1 | "$LOG_PREFIX" $(basename "$SCRIPT") >> "$LOG"
else
  # If LOG_PREFIX doesn't exist, use a simple timestamp instead
  $VENV_PYTHON "$SCRIPT" $ARGS 2>&1 | sed "s/^/[$(date '+%Y-%m-%d %H:%M:%S')] $(basename "$SCRIPT") | /" >> "$LOG"
fi