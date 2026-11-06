"""
Health, metrics, and policy discovery API router.
"""

from fastapi import APIRouter
from pathlib import Path
import time
from backend.schemas.api_models import HealthResponse
from backend.routers.chat import get_pipeline

router = APIRouter(prefix="/api", tags=["System"])
START_TIME = time.time()
POLICIES_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "policies"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    pipeline = get_pipeline()
    doc_count = len(pipeline.vector_store.documents) if pipeline.vector_store and pipeline.vector_store.documents else 0
    return {
        "status": "healthy",
        "service": "ShopAssist AI Backend",
        "version": "1.0.0",
        "indexed_documents": doc_count,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }


@router.get("/policies")
async def list_policies():
    """Lists available store policy documents and titles."""
    policies = []
    if POLICIES_DIR.exists():
        for p in sorted(POLICIES_DIR.glob("*.md")):
            lines = p.read_text(encoding="utf-8").splitlines()
            title = lines[0].replace("# ", "").strip() if lines else p.stem
            policies.append({
                "file": p.name,
                "title": title,
                "category": p.stem.split("_")[0].upper()
            })
    return {"count": len(policies), "policies": policies}

