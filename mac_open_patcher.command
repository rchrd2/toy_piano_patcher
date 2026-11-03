#!/bin/bash
# Double-click in Finder to open the patcher window.
cd "$(dirname "$0")" || exit 1

# Use the Python bundled in vendor/ (see vendor/README.md), so nothing needs installing.
if [ "$(uname -m)" = "arm64" ]; then
    bundled="vendor/python-mac-arm64/bin/python3.13"
else
    bundled="vendor/python-mac-x86_64/bin/python3.13"
fi

if [ -f "$bundled" ]; then
    # A downloaded zip marks every file as quarantined. Opening this launcher was your approval, so
    # clear the flag on the bundled Python too; otherwise macOS would block it separately.
    xattr -dr com.apple.quarantine vendor 2>/dev/null
    python="$bundled"
elif command -v python3 >/dev/null 2>&1; then
    echo "The bundled Python is missing, so using the system's python3."
    python=python3
else
    echo "The bundled Python is missing, and Python 3 was not found."
    echo "Download the patcher again, or install Python from https://www.python.org/downloads/"
    read -r -p "Press Return to close."
    exit 1
fi

"$python" -B toy_piano_patcher.py
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "The patcher stopped with an error (code $status)."
    read -r -p "Press Return to close."
fi
exit "$status"
