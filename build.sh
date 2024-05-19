#!/bin/bash

# Directory of the script
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)

# Navigate to the script directory
cd "$SCRIPT_DIR"

# Name of the virtual environment directory
VENV_DIR="venv"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install networkx in the virtual environment
pip install networkx

echo "NetworkX has been installed in the virtual environment"

# Deactivate the virtual environment
deactivate

echo "Setup is complete"
