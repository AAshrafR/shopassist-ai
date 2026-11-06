"""
Vercel Serverless Function entrypoint for ShopAssist AI FastAPI backend.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app as fastapi_app


class VercelPathNormalizer:
    """
    ASGI middleware ensuring that Vercel internal rewrites (like /api/index.py)
    or stripped prefixes route correctly to FastAPI routers using x-matched-path or raw path.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")

            # If Vercel rewrote path to /api/index.py or similar, use the matched incoming path
            if matched_path and matched_path.startswith("/api"):
                scope["path"] = matched_path
            elif not scope.get("path", "").startswith("/api") and not scope.get("path", "").startswith("/docs") and not scope.get("path", "").startswith("/openapi"):
                # Handle cases where /api was stripped (e.g. /chat -> /api/chat)
                scope["path"] = f"/api{scope['path']}"

        await self.app(scope, receive, send)


app = VercelPathNormalizer(fastapi_app)
