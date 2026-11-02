#!/bin/bash
# Double-click in Finder to open the patcher window.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Install it from https://www.python.org/downloads/"
    read -r -p "Press Return to close."
    exit 1
fi

python3 -B toy_piano_patcher.py
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "The patcher stopped with an error (code $status)."
    read -r -p "Press Return to close."
fi
exit "$status"
