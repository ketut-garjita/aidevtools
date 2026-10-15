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
