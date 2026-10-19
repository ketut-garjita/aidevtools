# Capability: Autonomous On-Call Incident Responder Agent

> **Rubric Alignment**: Satisfies **Criterion #12 (On-Call Agent)**.

## 1. Overview
The On-Call Responder Agent (`@oncall-responder`) is triggered when alerting thresholds detect real user impact (e.g. WebSocket connection drops >5%, 5xx error spikes, or unresponsive health endpoints). The agent inspects structured logs, executes diagnostic runbooks, applies automated fixes, and verifies recovery.

## 2. Trigger Envelope
```json
{
  "alert_id": "ALT-USER-IMPACT-001",
  "name": "High Chat Connection Drop Rate",
  "severity": "CRITICAL",
  "impact": "Shoppers unable to initiate or maintain real-time support chats",
  "trace_id": "tr-7f9a2b1c",
  "timestamp": 1729337500
}
```

## 3. Incident Execution & Remediation Workflow
1. **Wakeup & Diagnostic Assessment**:
   - Queries telemetry `/api/health` and Cloud Logging filtered by `trace_id` or `severity >= ERROR`.
   - Checks process state and active connections using `ops/health-check.sh`.
2. **Automated Remediation**:
   - Stale session leak / memory pressure $\to$ Triggers idle conversation resolution endpoint `/api/conversations/cleanup`.
   - Process freeze / port conflict $\to$ Issues restart signal or falls back to standby container replica.
3. **Verification & Post-Mortem**:
   - Runs `python3 -m unittest discover tests` and `ops/health-check.sh` to confirm zero user impact.
   - Posts incident resolution log with trace ID, root cause, and recovery duration.
