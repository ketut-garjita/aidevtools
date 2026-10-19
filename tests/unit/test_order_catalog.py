"""
Unit Tests for E-Commerce Order Catalog & Chat Store Logic
"""

import unittest
import sys
import os

# Add app_build to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app_build")))

from lib.mock_orders import lookup_order, get_all_orders_summary
from lib.chat_store import ChatStore


class TestOrderCatalogUnit(unittest.TestCase):

    def test_lookup_order_existing(self):
        order = lookup_order("ORD-1001")
        self.assertIsNotNone(order)
        self.assertEqual(order["customer_name"], "Alex Morgan")
        self.assertEqual(order["status"], "In Transit")

    def test_lookup_order_case_insensitive_and_hash(self):
        order = lookup_order("#ord-1001")
        self.assertIsNotNone(order)
        self.assertEqual(order["order_id"], "ORD-1001")

    def test_lookup_order_digits_only(self):
        order = lookup_order("1001")
        self.assertIsNotNone(order)
        self.assertEqual(order["order_id"], "ORD-1001")

    def test_lookup_order_nonexistent(self):
        order = lookup_order("ORD-9999")
        self.assertIsNone(order)

    def test_get_all_orders_summary(self):
        summary = get_all_orders_summary()
        self.assertIsInstance(summary, list)
        self.assertGreaterEqual(len(summary), 3)
        self.assertIn("order_id", summary[0])


class TestChatStoreUnit(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.store = ChatStore()

    async def test_create_and_get_conversation(self):
        conv = await self.store.get_or_create_conversation("cust_01", "Alice")
        self.assertEqual(conv["customer_name"], "Alice")
        self.assertEqual(conv["status"], "queued")
        self.assertEqual(conv["customer_id"], "cust_01")

    async def test_add_message(self):
        conv = await self.store.get_or_create_conversation("cust_02", "Bob")
        msg = await self.store.add_message(conv["id"], "customer", "Bob", "Hello support!")
        self.assertIsNotNone(msg)
        self.assertEqual(msg["sender"], "customer")
        self.assertEqual(msg["sender_name"], "Bob")
        self.assertEqual(msg["text"], "Hello support!")

        conv_fetched = await self.store.get_conversation(conv["id"])
        # Initial greeting + added message = 2 messages
        self.assertEqual(len(conv_fetched["messages"]), 2)

    async def test_assign_agent(self):
        conv = await self.store.get_or_create_conversation("cust_03", "Charlie")
        assigned = await self.store.assign_agent(conv["id"], "agent_01", "Agent Sarah")
        self.assertIsNotNone(assigned)
        self.assertEqual(assigned["status"], "active")
        self.assertEqual(assigned["assigned_agent"], "agent_01")

    async def test_resolve_conversation(self):
        conv = await self.store.get_or_create_conversation("cust_04", "David")
        resolved = await self.store.resolve_conversation(conv["id"])
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["status"], "resolved")


if __name__ == "__main__":
    unittest.main()
