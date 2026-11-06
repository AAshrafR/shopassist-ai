"""
Unit tests for business tools: order lookup and support ticket creation.
"""

import pytest
from src.tools.order_tool import lookup_order_status, extract_order_id
from src.tools.ticket_tool import create_support_ticket, list_recent_tickets


def test_extract_order_id():
    assert extract_order_id("Where is my order ORD-1001?") == "ORD-1001"
    assert extract_order_id("Status for #1002") == "ORD-1002"
    assert extract_order_id("1003 please") == "ORD-1003"
    assert extract_order_id("No number here") is None


def test_order_lookup_success():
    res = lookup_order_status("ORD-1001")
    assert res["success"] is True
    assert res["order_id"] == "ORD-1001"
    assert res["status"] == "Shipped"
    assert "Sarah Connor" in res["message"]


def test_order_lookup_not_found():
    res = lookup_order_status("ORD-9999")
    assert res["success"] is False
    assert "No order found" in res["message"]


def test_create_support_ticket():
    res = create_support_ticket(
        customer_name="Test Customer",
        customer_email="test@example.com",
        subject="Shipping delay inquiry",
        description="Package has not arrived.",
        category="SHIPPING",
        priority="High",
        order_id="ORD-1001"
    )
    assert res["success"] is True
    assert "TKT-" in res["ticket_id"]
    assert res["data"]["category"] == "SHIPPING"
    assert res["data"]["priority"] == "High"


def test_list_recent_tickets():
    res = list_recent_tickets(limit=5)
    assert res["success"] is True
    assert res["count"] >= 2

