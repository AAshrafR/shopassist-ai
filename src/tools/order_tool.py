"""
Order status lookup business tool for ShopAssist AI.
"""

from __future__ import annotations
import re
from typing import Dict, Any, Optional
from src.data.simulated_data import find_order, get_all_orders


def extract_order_id(text: str) -> Optional[str]:
    """Extracts order IDs like ORD-1001, ord-1002, ORD1003, or #1001 from user text."""
    match = re.search(r"\b(?:ORD-?|#)?(\d{4})\b", text, re.IGNORECASE)
    if match:
        return f"ORD-{match.group(1)}"
    match_named = re.search(r"\b(ORD-\w+)\b", text, re.IGNORECASE)
    if match_named:
        return match_named.group(1).upper()
    return None


def lookup_order_status(order_id_or_query: str) -> Dict[str, Any]:
    """
    Looks up order details in the business data store.
    Accepts explicit order ID (e.g. 'ORD-1001') or a natural language string.
    """
    clean_id = extract_order_id(order_id_or_query) or order_id_or_query.strip().upper()
    order = find_order(clean_id)

    if not order:
        return {
            "success": False,
            "order_id": clean_id,
            "message": f"No order found matching ID '{clean_id}'. Please verify your order number (e.g., ORD-1001).",
            "data": None
        }

    status = order.get("status", "Unknown")
    tracking = order.get("tracking_number") or "N/A"
    carrier = order.get("carrier") or "Pending carrier assignment"
    est_delivery = order.get("estimated_delivery") or "Pending"
    items_summary = ", ".join([f"{item['item_name']} (x{item['quantity']})" for item in order.get("items", [])])

    details_msg = (
        f"Order {order['order_id']} for {order['customer_name']} is currently **{status}**.\n"
        f"- Shipping Method: {order.get('shipping_method')}\n"
        f"- Carrier: {carrier}\n"
        f"- Tracking Number: `{tracking}`\n"
        f"- Estimated Delivery: {est_delivery}\n"
        f"- Items: {items_summary}\n"
        f"- Total: ${order.get('total_amount', 0.0):.2f}"
    )

    return {
        "success": True,
        "order_id": order["order_id"],
        "status": status,
        "message": details_msg,
        "data": order
    }

