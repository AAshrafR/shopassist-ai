"""
Vercel Serverless Function entrypoint for ShopAssist AI FastAPI backend.
"""

import sys
import urllib.parse
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app as fastapi_app


class VercelPathNormalizer:
    """
    ASGI middleware ensuring that Vercel rewrites with __route__ parameter,
    x-matched-path headers, or direct paths route correctly to FastAPI routers.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            target_path = None

            # 1. Check if __route__ parameter was passed via Vercel rewrite
            qs = scope.get("query_string", b"").decode("utf-8")
            if qs:
                params = urllib.parse.parse_qs(qs)
                if "__route__" in params and params["__route__"]:
                    target_path = params["__route__"][0]
                    filtered_params = {k: v for k, v in params.items() if k != "__route__"}
                    scope["query_string"] = urllib.parse.urlencode(filtered_params, doseq=True).encode("utf-8")

            # 2. Check x-matched-path header
            if not target_path:
                headers = dict(scope.get("headers", []))
                matched = headers.get(b"x-matched-path", b"").decode("utf-8")
                if matched and matched != "/api/index.py" and matched != "/api/index":
                    target_path = matched

            # 3. Fallback to raw scope path
            if not target_path:
                raw = scope.get("path", "/")
                if raw in ("/api/index.py", "/index.py", "/api/index"):
                    target_path = "/"
                else:
                    target_path = raw

            # 4. If an API endpoint was requested without /api prefix, normalize it
            api_endpoints = ("/chat", "/orders", "/tickets", "/health", "/policies")
            if any(target_path == ep or target_path.startswith(ep + "/") for ep in api_endpoints):
                target_path = f"/api{target_path}"

            scope["path"] = target_path

        await self.app(scope, receive, send)


app = VercelPathNormalizer(fastapi_app)
