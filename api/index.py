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

            # 1. Prefer original requested path from Vercel's x-matched-path header
            if matched_path:
                target_path = matched_path
            else:
                target_path = scope.get("path", "/")

            # 2. If path is internal Vercel script path (/api/index.py or /index.py), default to root /
            if target_path in ("/api/index.py", "/index.py", "/api/index"):
                target_path = "/"

            # 3. If an API endpoint was requested without /api prefix, normalize it
            api_endpoints = ("/chat", "/orders", "/tickets", "/health", "/policies")
            if any(target_path == ep or target_path.startswith(ep + "/") for ep in api_endpoints):
                target_path = f"/api{target_path}"

            scope["path"] = target_path

        await self.app(scope, receive, send)


app = VercelPathNormalizer(fastapi_app)
