#!/bin/bash

# Directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Save the current process ID to pid.log
echo "$$" > "$SCRIPT_DIR/pid.log"

# Run the Python script and redirect stderr to error.log
exec python3 "$SCRIPT_DIR/code/run_bot.py" 2>"$SCRIPT_DIR/error.log"
