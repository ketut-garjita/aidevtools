"""
Real-Time E-Commerce Customer Support Chat Server
FastAPI + WebSockets + Uvicorn
"""

import os
import json
import asyncio
from typing import Dict, Set, Optional, Any
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from lib.chat_store import chat_store
from lib.mock_orders import lookup_order, get_all_orders_summary

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Real-Time E-Commerce Customer Support Chat",
    version="1.0.0",
    description="Asynchronous Real-Time Chat Platform for E-Commerce Storefronts and Support Agents"
)

# Enable CORS for cross-origin storefront integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """Manages active WebSockets for customers and support agents."""

    def __init__(self):
        # conversation_id -> Set[WebSocket]
        self.conversation_rooms: Dict[str, Set[WebSocket]] = {}
        # All connected agent sockets
        self.agent_sockets: Set[WebSocket] = set()
        # websocket -> metadata dict (role, id, conversation_id, name)
        self.socket_meta: Dict[WebSocket, Dict[str, Any]] = {}

    def disconnect(self, websocket: WebSocket):
        meta = self.socket_meta.pop(websocket, None)
        if meta and meta.get("role") == "customer":
            conv_id = meta.get("conversation_id")
            if conv_id and conv_id in self.conversation_rooms:
                self.conversation_rooms[conv_id].discard(websocket)
                if not self.conversation_rooms[conv_id]:
                    del self.conversation_rooms[conv_id]
        elif meta and meta.get("role") == "agent":
            self.agent_sockets.discard(websocket)
        else:
            for room in list(self.conversation_rooms.values()):
                room.discard(websocket)
            self.agent_sockets.discard(websocket)

    async def send_to_socket(self, websocket: WebSocket, event_type: str, payload: dict):
        try:
            await websocket.send_text(json.dumps({"type": event_type, "payload": payload}))
        except Exception:
            pass

    async def broadcast_to_conversation(self, conversation_id: str, event_type: str, payload: dict):
        """Send event to all participants in a conversation and all connected agents."""
        msg_str = json.dumps({"type": event_type, "payload": payload})
        
        # 1. Send to customers in room
        sockets = list(self.conversation_rooms.get(conversation_id, []))
        for ws in sockets:
            try:
                await ws.send_text(msg_str)
            except Exception:
                pass

        # 2. Also send to all agents so their live views and previews update
        for aws in list(self.agent_sockets):
            if aws not in sockets:
                try:
                    await aws.send_text(msg_str)
                except Exception:
                    pass

    async def broadcast_to_agents(self, event_type: str, payload: dict):
        """Notify all connected support agents."""
        msg_str = json.dumps({"type": event_type, "payload": payload})
        for aws in list(self.agent_sockets):
            try:
                await aws.send_text(msg_str)
            except Exception:
                pass


manager = ConnectionManager()


# ---------------- REST API Endpoints ----------------

@app.get("/api/health")
async def health_check():
    online_agents = await chat_store.get_online_agents_count()
    conversations = await chat_store.list_conversations()
    return {
        "status": "healthy",
        "service": "ecommerce-customer-support-chat",
        "online_agents": online_agents,
        "active_conversations": len([c for c in conversations if c["status"] != "resolved"]),
        "total_conversations": len(conversations)
    }


@app.get("/api/orders")
async def list_demo_orders():
    """Return available demo orders for fast testing."""
    return {"orders": get_all_orders_summary()}


@app.get("/api/orders/{order_id}")
async def get_order_details(order_id: str):
    """Query simulated order status."""
    order = lookup_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order}


@app.get("/api/canned-responses")
async def get_canned_macros():
    return {"canned_responses": chat_store.get_canned_responses()}


@app.get("/api/conversations")
async def get_conversations():
    convs = await chat_store.list_conversations()
    return {"conversations": convs}


@app.post("/api/conversations/{conversation_id}/resolve")
async def resolve_conversation(conversation_id: str):
    conv = await chat_store.resolve_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Notify room participants and agents
    await manager.broadcast_to_conversation(
        conversation_id,
        "conversation_resolved",
        {"conversationId": conversation_id, "status": "resolved"}
    )
    all_convs = await chat_store.list_conversations()
    await manager.broadcast_to_agents("queue_update", {"conversations": all_convs})
    return {"status": "ok", "conversation": conv}


# ---------------- Real-Time WebSocket Handler ----------------

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_role = None
    current_conv_id = None
    current_user_id = None

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                continue

            event_type = data.get("type")
            payload = data.get("payload", {})

            # 1. Customer Session Initialization
            if event_type == "customer_init":
                customer_id = payload.get("customerId", "guest")
                name = payload.get("name", "Shopper")
                conv = await chat_store.get_or_create_conversation(customer_id, name)
                current_conv_id = conv["id"]
                current_role = "customer"
                current_user_id = customer_id

                if current_conv_id not in manager.conversation_rooms:
                    manager.conversation_rooms[current_conv_id] = set()
                manager.conversation_rooms[current_conv_id].add(websocket)
                manager.socket_meta[websocket] = {
                    "role": "customer",
                    "customer_id": customer_id,
                    "conversation_id": current_conv_id,
                    "name": name
                }

                # Send history & active conversation details back to customer
                online_agents = await chat_store.get_online_agents_count()
                await manager.send_to_socket(websocket, "session_ready", {
                    "conversation": conv,
                    "onlineAgents": online_agents
                })

                # Broadcast queue refresh to all agents
                all_convs = await chat_store.list_conversations()
                await manager.broadcast_to_agents("queue_update", {"conversations": all_convs})

            # 2. Agent Pool Connection
            elif event_type == "agent_join":
                agent_id = payload.get("agentId", "agent_1")
                agent_name = payload.get("agentName", "Support Rep")
                current_role = "agent"
                current_user_id = agent_id

                manager.agent_sockets.add(websocket)
                manager.socket_meta[websocket] = {
                    "role": "agent",
                    "agent_id": agent_id,
                    "name": agent_name
                }
                await chat_store.register_agent(agent_id, agent_name)

                # Send conversations list & macros to agent
                all_convs = await chat_store.list_conversations()
                await manager.send_to_socket(websocket, "agent_ready", {
                    "conversations": all_convs,
                    "cannedResponses": chat_store.get_canned_responses()
                })
                # Alert customers of agent presence
                for r_conv_id in manager.conversation_rooms:
                    await manager.broadcast_to_conversation(
                        r_conv_id,
                        "agent_presence",
                        {"onlineAgents": len(manager.agent_sockets)}
                    )

            # 3. Chat Message Transmission
            elif event_type == "send_message":
                conv_id = payload.get("conversationId") or current_conv_id
                sender = payload.get("sender", current_role or "customer")
                sender_name = payload.get("senderName", "Customer" if sender == "customer" else "Support Specialist")
                text = (payload.get("text") or "").strip()

                if not conv_id or not text:
                    continue

                # Add to chat store
                new_msg = await chat_store.add_message(conv_id, sender, sender_name, text)
                if new_msg:
                    await manager.broadcast_to_conversation(conv_id, "receive_message", new_msg)

                    # Update queue rankings for agents
                    all_convs = await chat_store.list_conversations()
                    await manager.broadcast_to_agents("queue_update", {"conversations": all_convs})

            # 4. Typing Indicator
            elif event_type == "typing":
                conv_id = payload.get("conversationId") or current_conv_id
                sender = payload.get("sender", current_role or "user")
                sender_name = payload.get("senderName", "User")
                is_typing = bool(payload.get("isTyping", False))

                if conv_id:
                    await manager.broadcast_to_conversation(conv_id, "typing_status", {
                        "conversationId": conv_id,
                        "sender": sender,
                        "senderName": sender_name,
                        "isTyping": is_typing
                    })

            # 5. Order Lookup via Chat
            elif event_type == "order_query":
                conv_id = payload.get("conversationId") or current_conv_id
                raw_order_id = payload.get("orderId", "")
                order = lookup_order(raw_order_id)

                if order:
                    card_text = (
                        f"📦 **Order Found: {order['order_id']}**\n"
                        f"• Status: {order['status']}\n"
                        f"• Carrier: {order['carrier']} ({order['tracking_number']})\n"
                        f"• ETA: {order['estimated_delivery']}\n"
                        f"• Latest: {order['last_update']}"
                    )
                    sys_msg = await chat_store.add_message(
                        conv_id, "system", "Order Assistant", card_text, is_system=True
                    )
                    await manager.broadcast_to_conversation(conv_id, "order_result", {
                        "found": True,
                        "order": order,
                        "message": sys_msg
                    })
                else:
                    not_found_text = (
                        f"❌ We could not find tracking information for '{raw_order_id}'. "
                        "Please verify your Order ID (e.g. #ORD-1001) or wait for a live agent."
                    )
                    sys_msg = await chat_store.add_message(
                        conv_id, "system", "Order Assistant", not_found_text, is_system=True
                    )
                    await manager.broadcast_to_conversation(conv_id, "order_result", {
                        "found": False,
                        "query": raw_order_id,
                        "message": sys_msg
                    })

            # 6. Claim / Assign Conversation by Agent
            elif event_type == "assign_agent":
                conv_id = payload.get("conversationId")
                agent_id = payload.get("agentId", current_user_id)
                agent_name = payload.get("agentName", "Support Specialist")

                updated = await chat_store.assign_agent(conv_id, agent_id, agent_name)
                if updated:
                    # Announce assignment
                    sys_msg = await chat_store.add_message(
                        conv_id, "system", "System",
                        f"Support Agent {agent_name} has joined the conversation.",
                        is_system=True
                    )
                    await manager.broadcast_to_conversation(conv_id, "receive_message", sys_msg)
                    all_convs = await chat_store.list_conversations()
                    await manager.broadcast_to_agents("queue_update", {"conversations": all_convs})

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
        if current_role == "agent" and current_user_id:
            await chat_store.unregister_agent(current_user_id)
            for r_conv_id in manager.conversation_rooms:
                await manager.broadcast_to_conversation(
                    r_conv_id,
                    "agent_presence",
                    {"onlineAgents": len(manager.agent_sockets)}
                )


# ---------------- Static File Servicing ----------------

# Mount static folder
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def serve_storefront():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"status": "Static index.html not yet scaffolded"}, status_code=200)
    return FileResponse(index_file)

@app.get("/agent.html")
async def serve_agent_dashboard():
    agent_file = STATIC_DIR / "agent.html"
    if not agent_file.exists():
        return JSONResponse({"status": "Static agent.html not yet scaffolded"}, status_code=200)
    return FileResponse(agent_file)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Real-Time E-Commerce Customer Support Chat on http://localhost:{port}")
    print(f"   - Storefront & Customer Widget: http://localhost:{port}/")
    print(f"   - Support Agent Dashboard:      http://localhost:{port}/agent.html")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
