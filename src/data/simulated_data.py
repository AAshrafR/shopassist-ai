"""
Simulated business data generator and management for ShopAssist AI.
Manages mock customer orders and support tickets in JSON storage.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "simulated"
ORDERS_FILE = DATA_DIR / "orders.json"
TICKETS_FILE = DATA_DIR / "tickets.json"


DEFAULT_ORDERS: List[Dict] = [
    {
        "order_id": "ORD-1001",
        "customer_name": "Sarah Connor",
        "customer_email": "sarah.connor@example.com",
        "status": "Shipped",
        "created_at": "2026-11-01T10:15:00Z",
        "shipping_method": "Expedited Two-Day",
        "carrier": "FedEx",
        "tracking_number": "FDX-998822110",
        "estimated_delivery": "2026-11-07",
        "shipping_address": "1244 Cyberdyne Way, Los Angeles, CA 90001",
        "total_amount": 149.99,
        "items": [
            {"item_name": "Wireless Noise-Cancelling Headphones", "quantity": 1, "price": 129.99},
            {"item_name": "Braided USB-C Fast Charging Cable", "quantity": 1, "price": 20.00}
        ]
    },
    {
        "order_id": "ORD-1002",
        "customer_name": "Alex Murphy",
        "customer_email": "alex.murphy@example.com",
        "status": "Delivered",
        "created_at": "2026-10-28T14:22:00Z",
        "shipping_method": "Standard Ground",
        "carrier": "UPS",
        "tracking_number": "UPS-1Z99999999",
        "estimated_delivery": "2026-11-03",
        "delivered_at": "2026-11-03T16:45:00Z",
        "shipping_address": "742 Evergreen Terrace, Detroit, MI 48201",
        "total_amount": 89.50,
        "items": [
            {"item_name": "Ergonomic Memory Foam Keyboard Wrist Rest", "quantity": 1, "price": 29.50},
            {"item_name": "Precision Optical Gaming Mouse", "quantity": 1, "price": 60.00}
        ]
    },
    {
        "order_id": "ORD-1003",
        "customer_name": "Elena Rostova",
        "customer_email": "elena.r@example.com",
        "status": "Processing",
        "created_at": "2026-11-05T09:05:00Z",
        "shipping_method": "Standard Ground",
        "carrier": "USPS",
        "tracking_number": "USPS-940010000000000000001",
        "estimated_delivery": "2026-11-09",
        "shipping_address": "350 5th Avenue, New York, NY 10118",
        "total_amount": 210.00,
        "items": [
            {"item_name": "Ultra-Wide 4K Monitor Arm", "quantity": 1, "price": 170.00},
            {"item_name": "Cable Management Sleeve Kit", "quantity": 2, "price": 40.00}
        ]
    },
    {
        "order_id": "ORD-1004",
        "customer_name": "David Miller",
        "customer_email": "david.m@example.com",
        "status": "Pending",
        "created_at": "2026-11-06T08:30:00Z",
        "shipping_method": "Priority Overnight",
        "carrier": "FedEx",
        "tracking_number": "FDX-PENDING-04",
        "estimated_delivery": "2026-11-08",
        "shipping_address": "100 Market St, San Francisco, CA 94105",
        "total_amount": 45.00,
        "items": [
            {"item_name": "Smart Thermostat Sensor", "quantity": 1, "price": 45.00}
        ]
    },
    {
        "order_id": "ORD-1005",
        "customer_name": "Maya Lin",
        "customer_email": "maya.lin@example.com",
        "status": "Cancelled",
        "created_at": "2026-10-25T11:00:00Z",
        "shipping_method": "Standard Ground",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": None,
        "shipping_address": "500 Pike Street, Seattle, WA 98101",
        "total_amount": 62.00,
        "items": [
            {"item_name": "Ceramic Pour-Over Coffee Dripper", "quantity": 1, "price": 32.00},
            {"item_name": "Organic Whole Bean Coffee 12oz", "quantity": 2, "price": 30.00}
        ]
    }
]


DEFAULT_TICKETS: List[Dict] = [
    {
        "ticket_id": "TKT-1001",
        "customer_name": "Sarah Connor",
        "customer_email": "sarah.connor@example.com",
        "order_id": "ORD-1001",
        "category": "SHIPPING",
        "priority": "Medium",
        "status": "Open",
        "subject": "Request delivery date confirmation",
        "description": "Customer inquired whether delivery can be completed prior to Friday evening.",
        "created_at": "2026-11-02T11:20:00Z",
        "updated_at": "2026-11-02T11:20:00Z"
    },
    {
        "ticket_id": "TKT-1002",
        "customer_name": "David Miller",
        "customer_email": "david.m@example.com",
        "order_id": "ORD-1004",
        "category": "PAYMENT",
        "priority": "High",
        "status": "In Progress",
        "subject": "Promo code was not applied during checkout",
        "description": "Customer entered 15% promotional voucher SAVE15, but invoice reflects full total.",
        "created_at": "2026-11-06T08:45:00Z",
        "updated_at": "2026-11-06T09:10:00Z"
    }
]


def ensure_data_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ORDERS_FILE.exists():
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_ORDERS, f, indent=2)
    if not TICKETS_FILE.exists():
        with open(TICKETS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_TICKETS, f, indent=2)


def get_all_orders() -> List[Dict]:
    ensure_data_files()
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_order(order_id: str) -> Optional[Dict]:
    clean_id = order_id.strip().upper()
    orders = get_all_orders()
    for o in orders:
        if o["order_id"].upper() == clean_id:
            return o
    return None


def get_all_tickets() -> List[Dict]:
    ensure_data_files()
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def add_ticket(
    customer_name: str,
    customer_email: str,
    subject: str,
    description: str,
    category: str = "GENERAL",
    priority: str = "Medium",
    order_id: Optional[str] = None
) -> Dict:
    ensure_data_files()
    tickets = get_all_tickets()
    new_num = 1001 + len(tickets)
    ticket_id = f"TKT-{new_num}"
    now_iso = datetime.now(timezone.utc).isoformat()
    new_ticket = {
        "ticket_id": ticket_id,
        "customer_name": customer_name.strip(),
        "customer_email": customer_email.strip(),
        "order_id": order_id.strip().upper() if order_id else None,
        "category": category.upper(),
        "priority": priority.capitalize(),
        "status": "Open",
        "subject": subject.strip(),
        "description": description.strip(),
        "created_at": now_iso,
        "updated_at": now_iso
    }
    tickets.append(new_ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)
    return new_ticket


if __name__ == "__main__":
    ensure_data_files()
    print(f"Initialized {len(get_all_orders())} orders and {len(get_all_tickets())} tickets.")

