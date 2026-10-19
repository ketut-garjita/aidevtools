"""
Zero-Dependency Integration Test Suite (Python Standard Library unittest)
Tests against the live running server at http://localhost:8000 or locally imported app.
"""

import unittest
import json
import urllib.request
import urllib.error

import os
import sys
import time
import subprocess

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")


class TestChatWorkflowIntegration(unittest.TestCase):
    server_process = None

    @classmethod
    def setUpClass(cls):
        # Check if server is already running
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/health")
            with urllib.request.urlopen(req, timeout=1):
                return
        except Exception:
            pass

        # Auto-spawn the FastAPI server for test execution
        server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app_build/server.py"))
        cls.server_process = subprocess.Popen([sys.executable, server_path])
        # Poll up to 10 seconds for health check to succeed
        for _ in range(20):
            time.sleep(0.5)
            try:
                req = urllib.request.Request(f"{BASE_URL}/api/health")
                with urllib.request.urlopen(req, timeout=1):
                    return
            except Exception:
                continue

    @classmethod
    def tearDownClass(cls):
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()

    def _fetch_json(self, path):
        req = urllib.request.Request(f"{BASE_URL}{path}", headers={"User-Agent": "TestClient/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            return data

    def test_01_health_check(self):
        """Verify service health endpoint."""
        data = self._fetch_json("/api/health")
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "ecommerce-customer-support-chat")
        self.assertIn("online_agents", data)
        self.assertIn("active_conversations", data)

    def test_02_demo_orders(self):
        """Verify demo orders catalog is queryable."""
        data = self._fetch_json("/api/orders")
        self.assertIn("orders", data)
        self.assertGreaterEqual(len(data["orders"]), 3)

    def test_03_order_lookup_success(self):
        """Verify lookup for existing demo order ORD-1001."""
        data = self._fetch_json("/api/orders/ORD-1001")
        order = data.get("order", {})
        self.assertEqual(order.get("order_id"), "ORD-1001")
        self.assertEqual(order.get("status"), "In Transit")
        self.assertEqual(order.get("carrier"), "FedEx Express")

    def test_04_order_lookup_404(self):
        """Verify 404 response for non-existent order."""
        req = urllib.request.Request(f"{BASE_URL}/api/orders/NONEXISTENT-999")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=5)
        self.assertEqual(ctx.exception.code, 404)

    def test_05_canned_macros(self):
        """Verify canned support macros."""
        data = self._fetch_json("/api/canned-responses")
        self.assertIn("canned_responses", data)
        self.assertGreaterEqual(len(data["canned_responses"]), 3)


if __name__ == "__main__":
    unittest.main()
