"""
Simulated E-Commerce Orders Database and Query Engine
"""

from typing import Optional, Dict, Any

MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_name": "Alex Morgan",
        "status": "In Transit",
        "status_color": "#3b82f6",
        "carrier": "FedEx Express",
        "tracking_number": "FX-884920194US",
        "estimated_delivery": "Tomorrow by 4:00 PM",
        "items": [
            {"name": "Ultra-light Wireless ANC Headphones", "qty": 1, "price": "$179.00"},
            {"name": "Braided USB-C Fast Charger Cable (2m)", "qty": 2, "price": "$29.00"}
        ],
        "total": "$237.00",
        "destination": "Austin, TX 78701",
        "last_update": "Departed regional fulfillment center, Dallas, TX"
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_name": "Sophia Bennett",
        "status": "Delivered",
        "status_color": "#10b981",
        "carrier": "UPS Ground",
        "tracking_number": "UPS-772183921US",
        "estimated_delivery": "Delivered Oct 14, 2:15 PM",
        "items": [
            {"name": "Minimalist Ceramic Pour-Over Coffee Kit", "qty": 1, "price": "$64.00"}
        ],
        "total": "$64.00",
        "destination": "Seattle, WA 98101",
        "last_update": "Front porch - Signed by customer"
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_name": "Jordan Lee",
        "status": "Processing",
        "status_color": "#f59e0b",
        "carrier": "USPS Priority",
        "tracking_number": "9400100000000000000000",
        "estimated_delivery": "Estimated Oct 18 - Oct 20",
        "items": [
            {"name": "Ergonomic Memory Foam Lumbar Support", "qty": 1, "price": "$45.00"},
            {"name": "Desk Mat Wool Felt Edition (Large)", "qty": 1, "price": "$38.00"}
        ],
        "total": "$83.00",
        "destination": "San Francisco, CA 94107",
        "last_update": "Order confirmed. Packing in progress at warehouse"
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "customer_name": "David Kim",
        "status": "Return Initiated",
        "status_color": "#ec4899",
        "carrier": "Return Drop-Off / UPS",
        "tracking_number": "RET-99214412",
        "estimated_delivery": "Pending parcel scan at dropoff",
        "items": [
            {"name": "Alpine Trail Running Shoes (Size 10.5)", "qty": 1, "price": "$135.00"}
        ],
        "total": "$135.00",
        "destination": "Denver, CO 80202",
        "last_update": "Pre-paid return shipping label generated and emailed"
    }
}


def lookup_order(raw_order_id: str) -> Optional[Dict[str, Any]]:
    """
    Search for an order using flexible string normalization.
    Accepts: 'ORD-1001', '#ORD-1001', 'ord-1001', or simply '1001'.
    """
    cleaned = raw_order_id.strip().upper().replace("#", "")
    if not cleaned.startswith("ORD-") and cleaned.isdigit():
        cleaned = f"ORD-{cleaned}"

    return MOCK_ORDERS.get(cleaned)


def get_all_orders_summary():
    """Return compact catalog of available demo orders for quick support testing."""
    return [
        {
            "order_id": order["order_id"],
            "status": order["status"],
            "customer_name": order["customer_name"],
            "total": order["total"]
        }
        for order in MOCK_ORDERS.values()
    ]
