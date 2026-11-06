#!/usr/bin/env python3
"""
Entry point to run the ShopAssist AI server directly:
    python run.py
"""

import sys
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting ShopAssist AI Customer Support Concierge")
    print("Web Interface & API available at: http://localhost:8000")
    print("Interactive API Docs available at: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
