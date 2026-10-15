"""
Model Context Protocol (MCP) Server for E-Commerce Chat System
Exposes custom tools for coding agents: order status diagnosis and queue inspection.
"""

import sys
import json

TOOLS = [
    {
        "name": "query_order_status",
        "description": "Look up real-time shipping carrier and fulfillment details for an order ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order identifier e.g. ORD-1001"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "get_support_metrics",
        "description": "Inspect active customer support queues, response latencies, and online agent counts.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_call_tool(name: str, arguments: dict):
    if name == "query_order_status":
        order_id = arguments.get("order_id", "").strip().upper()
        return {
            "status": "success",
            "order_id": order_id,
            "status_summary": "Order in transit via FedEx Express, expected tomorrow by 4:00 PM."
        }
    elif name == "get_support_metrics":
        return {
            "online_agents": 1,
            "queued_inquiries": 0,
            "active_chats": 1,
            "average_response_ms": 78
        }
    return {"error": f"Unknown tool {name}"}


if __name__ == "__main__":
    # Minimal standard MCP JSON-RPC responder for demonstration
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        print(json.dumps(TOOLS, indent=2))
    else:
        print("⚡ MCP E-Commerce Support Server running.")
