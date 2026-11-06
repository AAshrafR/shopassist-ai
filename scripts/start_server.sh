#!/usr/bin/env bash
# Start ShopAssist AI FastAPI backend server

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

if [ -d ".venv" ]; then
    PYTHON="$DIR/.venv/bin/python3"
else
    PYTHON="python3"
fi

export PYTHONPATH="$DIR"

echo "Starting ShopAssist AI on http://0.0.0.0:8000..."
exec "$PYTHON" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

