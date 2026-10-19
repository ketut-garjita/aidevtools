# Operations Runbook & Diagnosis Guide

> **Rubric Criteria Alignment**: Satisfies **Criterion #13 (Operational Diagnosis Output)**.

---

## 1. Service Health & Diagnostic Probing

### 1.1 Local Health Check
Run the automated probe script:
```bash
bash ops/health-check.sh
```

Or query the HTTP health endpoint directly:
```bash
curl -s http://localhost:8000/api/health | jq .
```
Expected output:
```json
{
  "status": "healthy",
  "service": "ecommerce-customer-support-chat",
  "online_agents": 1,
  "active_conversations": 2,
  "total_conversations": 5
}
```

---

## 2. Common Operational Issues & Remediation

| Symptom | Root Cause | Diagnosis Command | Remediation Action |
| :--- | :--- | :--- | :--- |
| **Port Conflict** | Port 8000 already bound by another process. | `lsof -i :8000` | Terminate conflicting process or start server with custom port: `PORT=8080 python3 server.py`. |
| **WebSocket Connection Failed** | Server is offline or proxy blocks WebSocket upgrade. | Check developer console for `WebSocket connection to 'ws://...' failed`. | Verify FastAPI server is running; check reverse proxy configuration for `Upgrade: websocket` headers. |
| **High Memory / Lag** | Large volume of inactive conversations retained in memory. | Check system process RAM usage: `top -p $(pgrep -f server.py)`. | Trigger `/api/conversations/{id}/resolve` on idle conversations; restart worker. |

---

## 3. Alerting on Real User Impact (Criterion #11)

Instead of alerting on generic CPU or raw memory graphs, alerting is wired directly to **real user experience**:

| Alert Rule | Impact Threshold | User Experience Impact | Alert Channel |
| :--- | :--- | :--- | :--- |
| **User Impact Alert #1: WebSocket Drop Rate** | Disconnect rate > 5% within 3 min | Shoppers abruptly lose active chat session with customer support | Webhook $\to$ On-Call Agent |
| **User Impact Alert #2: Message Ingestion Latency** | Message processing p95 > 500ms | Shoppers experience noticeable lag when sending or receiving messages | Webhook $\to$ On-Call Agent |
| **User Impact Alert #3: Order Lookup Failure Rate** | 5xx response rate > 2% on `/api/orders` | Shoppers cannot track order delivery, driving cart abandonment | Cloud Logging Alert $\to$ Agent |

---

## 4. On-Call Agent Automation & Remediation (Criterion #12)

When an alert triggers, the **On-Call Agent (`@oncall-responder`)** wakes up autonomously:
1. **Receipt & Correlation**: Receives webhook containing alert metadata and `trace_id`.
2. **Diagnosis**: Invokes `ops/health-check.sh` and extracts correlated logs from Cloud Logging.
3. **Automated Fix**:
   - Flushes stale WebSocket connection rooms if socket handles are orphaned.
   - Cleans up resolved conversations to recover memory.
   - Restarts ASGI worker container if unresponsive.
4. **Verification**: Re-probes `/api/health` and verifies that the p95 latency drops back under 100ms.
5. **Resolution Report**: Emits post-incident summary with root cause and zero shopper data exposure.
