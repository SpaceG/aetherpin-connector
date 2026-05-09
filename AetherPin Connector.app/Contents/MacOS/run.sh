#!/bin/bash
# AetherPin Connector — Mac App Launcher
# Double-click to start. Asks for API key + folder, then watches for FITS/XISF/SER files.

DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
VENV="$DIR/venv"
AGENT="$DIR/agent"

# ── Check Python ──────────────────────────────────────────────────────────
PYTHON=""
for p in python3.14 python3.13 python3.12 python3.11 python3 python; do
    if command -v "$p" &>/dev/null; then PYTHON="$p"; break; fi
done

if [ -z "$PYTHON" ]; then
    osascript -e 'display alert "Python not found" message "Please install Python 3.11+ from python.org" as critical'
    exit 1
fi

# ── Setup venv if needed ─────────────────────────────────────────────────
if [ ! -f "$VENV/bin/activate" ]; then
    osascript -e 'display notification "Setting up environment…" with title "AetherPin Connector"'
    "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install --quiet astropy watchdog requests
fi

source "$VENV/bin/activate"

# ── Ask for API key ──────────────────────────────────────────────────────
KEY=$(osascript -e 'text returned of (display dialog "Paste your AetherPin API key:" default answer "ap_" with title "AetherPin Connector" with icon note)')

if [ -z "$KEY" ]; then
    exit 0
fi

if [[ "$KEY" != ap_* ]]; then
    osascript -e 'display alert "Invalid API Key" message "The key must start with ap_" as critical'
    exit 1
fi

# ── Ask for FITS folder ─────────────────────────────────────────────────
FOLDER=$(osascript -e 'POSIX path of (choose folder with prompt "Select the folder where your capture software saves images (FITS, XISF, SER)")')

if [ -z "$FOLDER" ]; then
    exit 0
fi

# ── Run connector ────────────────────────────────────────────────────────
osascript -e "display notification \"Watching: $FOLDER\" with title \"AetherPin Connector\" subtitle \"Pin active\""

# Open Terminal so user can see output and Ctrl+C to stop
osascript -e "
tell application \"Terminal\"
    activate
    do script \"cd '$DIR' && source venv/bin/activate && python -m agent --key '$KEY' --watch '$FOLDER'\"
end tell
"
