#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd) && echo "$$" > "$SCRIPT_DIR/pid.log" && exec python3 "$SCRIPT_DIR/code/bot.py" 2>"$SCRIPT_DIR/error.log"
