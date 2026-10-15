"""
In-Memory Asynchronous Chat Store with Thread-Safe Concurrency Locks
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any


class ChatStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        
        # conversation_id -> conversation dict
        # {
        #   "id": str,
        #   "customer_id": str,
        #   "customer_name": str,
        #   "status": "queued" | "active" | "resolved",
        #   "assigned_agent": Optional[str],
        #   "created_at": float,
        #   "updated_at": float,
        #   "messages": list,
        #   "metadata": dict
        # }
        self._conversations: Dict[str, Dict[str, Any]] = {}
        
        # customer_id -> active conversation_id
        self._customer_active_conversation: Dict[str, str] = {}
        
        # Active connected agents: agent_id -> agent info
        self._active_agents: Dict[str, Dict[str, Any]] = {}

        # Standard canned responses for support efficiency
        self._canned_responses = [
            {"id": "c1", "title": "Friendly Greeting", "text": "Hello! Welcome to our store support. How can I assist you today?"},
            {"id": "c2", "title": "Ask for Order ID", "text": "Could you please provide your Order ID (e.g. #ORD-1001) so I can pull up your shipment details?"},
            {"id": "c3", "title": "Shipping Timelines", "text": "Standard shipping usually takes 2-4 business days. Expedited priority arrives in 1-2 business days."},
            {"id": "c4", "title": "Return Policy", "text": "We offer a 30-day hassle-free return policy on all unworn items with original tags and packaging intact."},
            {"id": "c5", "title": "Issue Resolved Wrap-up", "text": "I'm glad we could resolve that for you! Is there anything else I can help with today?"}
        ]

    async def get_or_create_conversation(self, customer_id: str, customer_name: str = "Shopper") -> Dict[str, Any]:
        async with self._lock:
            # Check if customer already has an active or queued conversation
            existing_id = self._customer_active_conversation.get(customer_id)
            if existing_id and existing_id in self._conversations:
                conv = self._conversations[existing_id]
                if conv["status"] != "resolved":
                    return conv

            # Create new conversation
            conv_id = f"conv_{uuid.uuid4().hex[:8]}"
            now = time.time()
            conv = {
                "id": conv_id,
                "customer_id": customer_id,
                "customer_name": customer_name,
                "status": "queued",
                "assigned_agent": None,
                "created_at": now,
                "updated_at": now,
                "messages": [
                    {
                        "id": f"msg_{uuid.uuid4().hex[:8]}",
                        "conversation_id": conv_id,
                        "sender": "system",
                        "sender_name": "Support Bot",
                        "text": f"Welcome {customer_name}! An agent has been alerted. You can also type your Order ID for instant tracking.",
                        "timestamp": now,
                        "is_system": True
                    }
                ],
                "metadata": {}
            }
            self._conversations[conv_id] = conv
            self._customer_active_conversation[customer_id] = conv_id
            return conv

    async def add_message(self, conversation_id: str, sender: str, sender_name: str, text: str, is_system: bool = False) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            
            conv = self._conversations[conversation_id]
            now = time.time()
            msg = {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "conversation_id": conversation_id,
                "sender": sender,
                "sender_name": sender_name,
                "text": text,
                "timestamp": now,
                "is_system": is_system
            }
            conv["messages"].append(msg)
            conv["updated_at"] = now
            return msg

    async def assign_agent(self, conversation_id: str, agent_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            conv = self._conversations[conversation_id]
            conv["assigned_agent"] = agent_id
            conv["status"] = "active"
            conv["updated_at"] = time.time()
            return conv

    async def resolve_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            conv = self._conversations[conversation_id]
            conv["status"] = "resolved"
            conv["updated_at"] = time.time()
            return conv

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._conversations.get(conversation_id)

    async def list_conversations(self) -> List[Dict[str, Any]]:
        async with self._lock:
            # Sort newest updated first
            return sorted(
                list(self._conversations.values()),
                key=lambda c: c["updated_at"],
                reverse=True
            )

    async def register_agent(self, agent_id: str, agent_name: str):
        async with self._lock:
            self._active_agents[agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "online_since": time.time(),
                "status": "online"
            }

    async def unregister_agent(self, agent_id: str):
        async with self._lock:
            self._active_agents.pop(agent_id, None)

    async def get_online_agents_count(self) -> int:
        async with self._lock:
            return len(self._active_agents)

    def get_canned_responses(self) -> List[Dict[str, str]]:
        return self._canned_responses


# Singleton global chat store instance
chat_store = ChatStore()
