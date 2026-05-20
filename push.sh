#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

git add .
git status

echo ""
read -p "Commit message: " msg
if [ -z "$msg" ]; then
    echo "Aborted: commit message cannot be empty."
    exit 1
fi

git commit -m "$msg"
git push
echo "Done!"
