"""
Integration tests for FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ShopAssist AI Backend"
    assert data["indexed_documents"] > 0


def test_list_policies_endpoint():
    response = client.get("/api/policies")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 5


def test_orders_endpoints():
    # List orders
    res_list = client.get("/api/orders")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 5

    # Get specific order
    res_single = client.get("/api/orders/ORD-1001")
    assert res_single.status_code == 200
    data = res_single.json()
    assert data["success"] is True
    assert data["order_id"] == "ORD-1001"

    # Not found order
    res_missing = client.get("/api/orders/ORD-9999")
    assert res_missing.status_code == 404


def test_tickets_endpoints():
    # Create ticket
    payload = {
        "customer_name": "Alice Smith",
        "customer_email": "alice@example.com",
        "subject": "Missing items in package",
        "description": "Item was omitted from my box.",
        "category": "ORDER",
        "priority": "Medium",
        "order_id": "ORD-1003"
    }
    res_create = client.post("/api/tickets", json=payload)
    assert res_create.status_code == 201
    data = res_create.json()
    assert data["success"] is True
    assert "TKT-" in data["ticket_id"]

    # List tickets
    res_list = client.get("/api/tickets")
    assert res_list.status_code == 200
    assert res_list.json()["count"] >= 1


def test_chat_endpoint_rag():
    payload = {"message": "What is the return policy?"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["answer"]) > 0
    assert len(data["sources"]) > 0


def test_chat_endpoint_tool():
    payload = {"message": "Track order ORD-1001"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tool_call"] is not None
    assert data["tool_call"]["tool_name"] == "order_lookup"

