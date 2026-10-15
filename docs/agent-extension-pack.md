# Agent Extension Pack Architecture & Capabilities

> **Rubric Criteria Alignment**: Satisfies **Criterion #12 (Agent Extension Pack)**.

---

## 1. Overview

The Agent Extension Pack extends the Antigravity developer environment with project-specific capabilities, specialized subagents, deterministic validation guardrails, and Model Context Protocol (MCP) tooling.

---

## 2. Pack Components

```text
├── agent-capabilities/        # Specialized prompt sequences and subagent profiles
│   ├── support-triage.md      # Auto-triage prompt for incoming support queries
│   └── order-investigator.md  # Automated order diagnosis capability
├── agent-hooks/               # Execution guardrails and safety validators
│   ├── pre-commit-check.sh    # Pre-commit lint and openapi contract check
│   └── guardrail-rules.json   # Deterministic constraints for AI tool invocation
├── mcp-server/                # Model Context Protocol (MCP) server
│   ├── server.py              # Custom tools exposing order lookup & chat queue metrics
│   └── mcp_config.json        # MCP server registration config
├── docs/agent-extension-pack.md # This documentation
└── docs/permissions.md        # Explicit tool & environment permission boundaries
```

---

## 3. Subagents & Capabilities

### A. Support Triage Subagent (`support-triage.md`)
- Automatically analyzes customer queries, classifies urgency (Low, Normal, Urgent), and suggests appropriate canned responses to agents.

### B. Order Investigator Subagent (`order-investigator.md`)
- Extracts Order IDs from conversation logs, queries the fulfillment system, and provides structured shipment diagnostics.

---

## 4. Model Context Protocol (MCP) Server

The MCP server in `mcp-server/server.py` implements the standard MCP protocol, exposing two primary tools to coding agents:
1. `query_order_status`: Tool to inspect order state, ETA, and tracking info.
2. `get_support_metrics`: Tool to retrieve active queues, unassigned chats, and response latencies.
