"""
Orders API router for looking up simulated orders.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from src.tools.order_tool import lookup_order_status
from src.data.simulated_data import get_all_orders

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_orders():
    """Returns all simulated business orders."""
    return get_all_orders()


@router.get("/{order_id}")
async def get_order_by_id(order_id: str):
    """Looks up specific order by ID."""
    res = lookup_order_status(order_id)
    if not res["success"]:
        raise HTTPException(status_code=404, detail=res["message"])
    return res

