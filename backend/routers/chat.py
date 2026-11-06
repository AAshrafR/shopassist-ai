"""
Chat router handling RAG queries, tool invocations, and response formatting.
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.api_models import ChatRequest, ChatResponse
from src.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Singleton pipeline instance
_rag_pipeline: RAGPipeline = None


def get_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


@router.post("", response_model=ChatResponse)
async def process_chat(request: ChatRequest, pipeline: RAGPipeline = Depends(get_pipeline)):
    try:
        result = pipeline.run(
            query=request.message,
            customer_name=request.customer_name,
            customer_email=request.customer_email
        )
        result["session_id"] = request.session_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing inquiry: {str(e)}")

