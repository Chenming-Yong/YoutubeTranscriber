#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
    echo "Setup complete."
fi

# Prompt for language
echo "Language: [1] Mandarin (default)  [2] English"
read -p "Choose (1/2): " lang_choice
if [ "$lang_choice" = "2" ]; then
    LANG_FLAG="--language en"
else
    LANG_FLAG="--language zh"
fi

# Activate and run
source "$VENV_DIR/bin/activate"
python "$SCRIPT_DIR/transcribe.py" $LANG_FLAG "$@"
