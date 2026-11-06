"""
Support ticket creation business tool for ShopAssist AI.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from src.data.simulated_data import add_ticket, get_all_tickets


def create_support_ticket(
    customer_name: str,
    customer_email: str,
    subject: str,
    description: str,
    category: str = "GENERAL",
    priority: str = "Medium",
    order_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a new support ticket in the customer support system.
    """
    if not customer_name:
        customer_name = "Valued Customer"
    if not customer_email or "@" not in customer_email:
        customer_email = "customer@example.com"
    if not subject:
        subject = "Customer Support Inquiry"
    if not description:
        description = "Assistance requested via ShopAssist AI assistant."

    ticket = add_ticket(
        customer_name=customer_name,
        customer_email=customer_email,
        subject=subject,
        description=description,
        category=category,
        priority=priority,
        order_id=order_id
    )

    msg = (
        f"Support ticket **{ticket['ticket_id']}** has been successfully created!\n"
        f"- Subject: {ticket['subject']}\n"
        f"- Category: {ticket['category']}\n"
        f"- Priority: {ticket['priority']}\n"
        f"- Customer: {ticket['customer_name']} ({ticket['customer_email']})\n"
        f"- Status: Open (Our support team will respond within 24 hours)."
    )

    return {
        "success": True,
        "ticket_id": ticket["ticket_id"],
        "message": msg,
        "data": ticket
    }


def list_recent_tickets(limit: int = 10) -> Dict[str, Any]:
    tickets = get_all_tickets()
    recent = list(reversed(tickets))[:limit]
    return {
        "success": True,
        "count": len(tickets),
        "tickets": recent
    }

