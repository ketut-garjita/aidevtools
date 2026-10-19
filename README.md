# ⚡ Aura Gear: Real-Time E-Commerce Customer Support Platform

[![CI/CD Pipeline](https://github.com/ketut-garjita/aidevtools/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ketut-garjita/aidevtools/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> An asynchronous, ultra-low latency customer support chat platform built specifically for modern e-commerce storefronts. Features an embeddable customer widget with live simulated order tracking and a multi-pane support agent command center.

### 🌐 Live Production Deployment (Cloud Run - Criterion #10)
- 🛍️ **Storefront & Live Customer Chat**: [https://appbuild-607895321006.asia-southeast2.run.app](https://appbuild-607895321006.asia-southeast2.run.app)
- 🎧 **Support Agent Command Console**: [https://appbuild-607895321006.asia-southeast2.run.app/agent.html](https://appbuild-607895321006.asia-southeast2.run.app/agent.html)
- 🩺 **API Health Check**: [https://appbuild-607895321006.asia-southeast2.run.app/api/health](https://appbuild-607895321006.asia-southeast2.run.app/api/health)

---

## 1. Problem Description (Peer Review Criterion #1)

Online retail shoppers frequently abandon their shopping carts when they cannot obtain instantaneous answers regarding:
- Real-time parcel tracking and shipping carrier timelines.
- Return and exchange policies.
- Sizing, specifications, and inventory availability.

Traditional support methods (ticketing portals, contact forms, delayed email queues) introduce friction that directly depresses conversion rates. **Aura Gear Support** solves this with an instant, embeddable real-time customer concierge and an integrated support agent dashboard.

---

## 2. AI-Assisted Development Workflow (Peer Review Criterion #2)

This project was engineered using the **Autonomous Developer Pipeline** in Antigravity:

```text
[ @pm (Product Manager) ] 
       │  Writes product-spec.md & openapi.yaml
       ▼
[ Human Approval Gate ] ──► (Feedback & Iteration: "Use Python instead of Node")
       │  Approved!
       ▼
[ @engineer (Full-Stack) ] ──► Implements backend, frontend, & state stores
       ▼
[ @qa (QA & Security) ]   ──► Hunts bugs, verifies WebSockets, writes tests
       ▼
[ @devops (DevOps Master) ]──► Containerizes via Docker, configures CI/CD & Runbooks
       ▼
[ @specialist (Agent Ops) ]──► Packages agent capabilities, hooks, & MCP tools
```

- **Prompts & Delegation**: Work was delegated autonomously using role definitions in [`.agents/agents.md`](file:///home/deai/zoomcamp/myprojects/aidevtools/.agents/agents.md) and custom skills in [`.agents/skills/`](file:///home/deai/zoomcamp/myprojects/aidevtools/.agents/skills/).
- **Context Governance**: Master repository rules and grading criteria were enforced via [AGENTS.md](file:///home/deai/zoomcamp/myprojects/aidevtools/AGENTS.md).
- **Human Verification**: An interactive approval gate allowed real-time steering of the tech stack from Node.js to Python before code synthesis began.

---

## 3. Technologies & System Architecture (Peer Review Criterion #3)

- **Backend**: Python 3.10+ with **FastAPI** & **Uvicorn** running asynchronous native WebSockets (`fastapi.WebSocket`).
- **Frontend**: Vanilla JavaScript and modern CSS Glassmorphic Design System (zero build overhead, <150KB bundle).
- **API Contract**: OpenAPI 3.0.3 specification in [`openapi.yaml`](file:///home/deai/zoomcamp/myprojects/aidevtools/openapi.yaml).
- **Containerization**: Multi-stage `Dockerfile` and root [`docker-compose.yml`](file:///home/deai/zoomcamp/myprojects/aidevtools/docker-compose.yml).
- **CI/CD**: GitHub Actions workflow in [`.github/workflows/ci-cd.yml`](file:///home/deai/zoomcamp/myprojects/aidevtools/.github/workflows/ci-cd.yml).
- **Agent Extensions**: Custom capabilities, guardrail hooks, and MCP tools in `agent-capabilities/`, `agent-hooks/`, and `mcp-server/`.

For complete architectural diagrams and sequence flows, see [docs/architecture.md](file:///home/deai/zoomcamp/myprojects/aidevtools/docs/architecture.md).

---

## 4. Quick Start & Reproducibility (Peer Review Criterion #14)

### Method A: Run Locally in Under 2 Minutes

```bash
# 1. Navigate to the application build directory
cd app_build

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the server
python3 server.py
```

Open your browser to:
- 🛍️ **Storefront & Customer Chat Widget**: [http://localhost:8000/](http://localhost:8000/)
- 🎧 **Support Agent Dashboard**: [http://localhost:8000/agent.html](http://localhost:8000/agent.html)
- 🩺 **Health Check API**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Method B: Run via Docker Compose (Criterion #8)

```bash
# Build and fire up the containers
docker compose up --build
```

---

## 5. Running Automated Tests (Criteria #4, #6, #9)

```bash
# Run the integration test suite (zero external dependencies required)
python3 tests/integration/test_chat_workflow.py
```

---

## 6. Repository Layout (Criterion A)

```text
├── README.md                          # Project overview & reproduction guide
├── product-spec.md                    # Technical specification & requirements
├── AGENTS.md                          # Master agent instructions & peer review rubric
├── openapi.yaml                       # API contract governing endpoints & payloads
├── docker-compose.yml                 # Multi-service container orchestration
├── .github/workflows/ci-cd.yml        # Automated CI/CD pipeline
├── app_build/                         # Production application build
│   ├── server.py                      # FastAPI + WebSocket server
│   ├── Dockerfile                     # Multi-stage container image
│   ├── lib/                           # Store & mock fulfillment engines
│   └── static/                        # Storefront & Agent console assets
├── tests/integration/                 # End-to-end integration tests
├── docs/                              # Architecture, extensions, permissions
├── security/                          # Security audits & AI data governance
├── ops/                               # Runbooks & operational health probes
├── agent-capabilities/                # Specialized agent prompts & workflows
├── agent-hooks/                       # Pre-commit guardrails & schema validators
└── mcp-server/                        # Model Context Protocol server & tools
```

## 7. 🚀 Cloud Run Production Deployment
- **Storefront & Live Chat Widget**: [https://appbuild-607895321006.asia-southeast2.run.app](https://appbuild-607895321006.asia-southeast2.run.app)

- **Support Agent Command Console**: [https://appbuild-607895321006.asia-southeast2.run.app/agent.html](https://appbuild-607895321006.asia-southeast2.run.app/agent.html)

- **API Health Check**: [https://appbuild-607895321006.asia-southeast2.run.app/api/health](https://appbuild-607895321006.asia-southeast2.run.app/api/health)

