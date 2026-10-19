"""
Persistent Asynchronous Chat Store with SQLite & Thread-Safe Concurrency Locks
"""

import os
import json
import sqlite3
import asyncio
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

DEFAULT_DB_PATH = str(Path(__file__).resolve().parent.parent / "chat.db")


class ChatStore:
    def __init__(self, db_path: Optional[str] = None):
        self._lock = asyncio.Lock()
        self.db_path = db_path or os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)
        
        # In-memory fast cache: conversation_id -> conversation dict
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

        # Initialize SQLite tables and hydrate cache
        self._init_sqlite()
        self._hydrate_from_sqlite()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        """Create persistent database tables for conversations and messages if not exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_agent TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    metadata TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    sender_name TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    is_system INTEGER NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            conn.commit()

    def _hydrate_from_sqlite(self):
        """Hydrate in-memory cache from persistent SQLite on startup."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations ORDER BY created_at ASC")
            rows = cursor.fetchall()

            for row in rows:
                conv_id = row["id"]
                conv = {
                    "id": conv_id,
                    "customer_id": row["customer_id"],
                    "customer_name": row["customer_name"],
                    "status": row["status"],
                    "assigned_agent": row["assigned_agent"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "messages": [],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
                self._conversations[conv_id] = conv
                if conv["status"] != "resolved":
                    self._customer_active_conversation[conv["customer_id"]] = conv_id

            # Hydrate messages
            cursor.execute("SELECT * FROM messages ORDER BY timestamp ASC")
            msg_rows = cursor.fetchall()
            for msg_row in msg_rows:
                cid = msg_row["conversation_id"]
                if cid in self._conversations:
                    self._conversations[cid]["messages"].append({
                        "id": msg_row["id"],
                        "conversation_id": cid,
                        "sender": msg_row["sender"],
                        "sender_name": msg_row["sender_name"],
                        "text": msg_row["text"],
                        "timestamp": msg_row["timestamp"],
                        "is_system": bool(msg_row["is_system"])
                    })

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
            welcome_msg = {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "conversation_id": conv_id,
                "sender": "system",
                "sender_name": "Support Bot",
                "text": f"Welcome {customer_name}! An agent has been alerted. You can also type your Order ID for instant tracking.",
                "timestamp": now,
                "is_system": True
            }

            conv = {
                "id": conv_id,
                "customer_id": customer_id,
                "customer_name": customer_name,
                "status": "queued",
                "assigned_agent": None,
                "created_at": now,
                "updated_at": now,
                "messages": [welcome_msg],
                "metadata": {}
            }

            # Persist to SQLite
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (id, customer_id, customer_name, status, assigned_agent, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (conv_id, customer_id, customer_name, "queued", None, now, now, "{}"))
                cursor.execute("""
                    INSERT INTO messages (id, conversation_id, sender, sender_name, text, timestamp, is_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (welcome_msg["id"], conv_id, "system", "Support Bot", welcome_msg["text"], now, 1))
                conn.commit()

            self._conversations[conv_id] = conv
            self._customer_active_conversation[customer_id] = conv_id
            return conv

    async def add_message(self, conversation_id: str, sender: str, sender_name: str, text: str, is_system: bool = False) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            
            conv = self._conversations[conversation_id]
            now = time.time()
            msg_id = f"msg_{uuid.uuid4().hex[:8]}"
            msg = {
                "id": msg_id,
                "conversation_id": conversation_id,
                "sender": sender,
                "sender_name": sender_name,
                "text": text,
                "timestamp": now,
                "is_system": is_system
            }
            conv["messages"].append(msg)
            conv["updated_at"] = now

            # Persist to SQLite
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (id, conversation_id, sender, sender_name, text, timestamp, is_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (msg_id, conversation_id, sender, sender_name, text, now, 1 if is_system else 0))
                cursor.execute("""
                    UPDATE conversations SET updated_at = ? WHERE id = ?
                """, (now, conversation_id))
                conn.commit()

            return msg

    async def assign_agent(self, conversation_id: str, agent_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            conv = self._conversations[conversation_id]
            now = time.time()
            conv["assigned_agent"] = agent_id
            conv["status"] = "active"
            conv["updated_at"] = now

            # Persist to SQLite
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE conversations SET assigned_agent = ?, status = 'active', updated_at = ? WHERE id = ?
                """, (agent_id, now, conversation_id))
                conn.commit()

            return conv

    async def resolve_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            if conversation_id not in self._conversations:
                return None
            conv = self._conversations[conversation_id]
            now = time.time()
            conv["status"] = "resolved"
            conv["updated_at"] = now

            # Persist to SQLite
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE conversations SET status = 'resolved', updated_at = ? WHERE id = ?
                """, (now, conversation_id))
                conn.commit()

            return conv

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._conversations.get(conversation_id)

    async def list_conversations(self) -> List[Dict[str, Any]]:
        async with self._lock:
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
