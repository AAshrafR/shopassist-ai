"""
Pydantic API schemas for request/response validation in ShopAssist AI.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer message or query", json_schema_extra={"example": "Where is my order ORD-1001?"})
    customer_name: Optional[str] = Field(None, description="Optional customer display name", json_schema_extra={"example": "Sarah Connor"})
    customer_email: Optional[str] = Field(None, description="Optional customer email", json_schema_extra={"example": "sarah@example.com"})
    session_id: Optional[str] = Field(None, description="Unique session identifier for the conversation")


class SourceReference(BaseModel):
    title: str
    category: str
    chunk_id: str
    source_file: str
    relevance_score: float


class ToolCallResult(BaseModel):
    tool_name: str
    status: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceReference] = []
    tool_call: Optional[ToolCallResult] = None
    latency_ms: float
    session_id: Optional[str] = None


class TicketCreateRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, json_schema_extra={"example": "John Doe"})
    customer_email: str = Field(..., json_schema_extra={"example": "john@example.com"})
    subject: str = Field(..., min_length=3, json_schema_extra={"example": "Inquiry about order delivery"})
    description: str = Field(..., min_length=5, json_schema_extra={"example": "My package was marked delivered but not received."})
    category: Optional[str] = Field("SUPPORT", json_schema_extra={"example": "SHIPPING"})
    priority: Optional[str] = Field("Medium", json_schema_extra={"example": "High"})
    order_id: Optional[str] = Field(None, json_schema_extra={"example": "ORD-1001"})


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    indexed_documents: int
    uptime_seconds: float
