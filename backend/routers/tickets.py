"""
Tickets API router for creating and listing support tickets.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.schemas.api_models import TicketCreateRequest
from src.tools.ticket_tool import create_support_ticket, list_recent_tickets

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.get("", response_model=Dict[str, Any])
async def get_tickets():
    """Lists current support tickets."""
    return list_recent_tickets(limit=50)


@router.post("", status_code=201)
async def create_ticket(req: TicketCreateRequest):
    """Creates a new support ticket in the simulated system."""
    res = create_support_ticket(
        customer_name=req.customer_name,
        customer_email=req.customer_email,
        subject=req.subject,
        description=req.description,
        category=req.category or "SUPPORT",
        priority=req.priority or "Medium",
        order_id=req.order_id
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail="Failed to create ticket.")
    return res

