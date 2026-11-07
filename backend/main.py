"""
FastAPI application entry point for ShopAssist AI.
Integrates RAG retrieval, business tools, REST endpoints,
logging middleware, and static frontend hosting.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routers import chat, orders, tickets, health
from src.monitoring.logger import RequestLoggingMiddleware, logger

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ShopAssist AI backend server initialized and ready.")
    yield
    logger.info("ShopAssist AI backend server shutting down.")


app = FastAPI(
    title="ShopAssist AI API",
    description="RAG-Powered Intelligent E-Commerce Customer Support System with Business Tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration for external frontend / Vercel cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom telemetry & request duration logging
app.add_middleware(RequestLoggingMiddleware)

# Register REST Routers
app.include_router(chat.router)
app.include_router(orders.router)
app.include_router(tickets.router)
app.include_router(health.router)

# Resilient static asset path resolver
def get_static_path(filename: str) -> Optional[Path]:
    for directory in [
        FRONTEND_DIR,
        BASE_DIR / "public",
        Path.cwd() / "frontend",
        Path.cwd() / "public",
        Path("/var/task/frontend"),
        Path("/var/task/public"),
    ]:
        candidate = directory / filename
        if candidate.exists():
            return candidate
    return None


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    f = get_static_path("index.html")
    if f and f.exists():
        return FileResponse(f)
    return {"message": "ShopAssist AI API is running. Access API docs at /docs"}


@app.get("/style.css", include_in_schema=False)
async def serve_css():
    f = get_static_path("style.css")
    if f and f.exists():
        return FileResponse(f, media_type="text/css")
    return {"error": "style.css not found"}


@app.get("/app.js", include_in_schema=False)
async def serve_js():
    f = get_static_path("app.js")
    if f and f.exists():
        return FileResponse(f, media_type="application/javascript")
    return {"error": "app.js not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
