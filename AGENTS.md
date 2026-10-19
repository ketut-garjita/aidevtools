# Project Governance & Agent Evaluation Guidelines: AGENTS.md

> **Master Specification for AI-Assisted Development & Peer Review Compliance**  
> This document establishes mandatory repository standards, architecture rules, and evaluation benchmarks. All autonomous agents (`@pm`, `@engineer`, `@qa`, `@devops`, `@specialist`) and human contributors must strictly follow these instructions to guarantee a maximum-score peer review evaluation.

---

## Part A: Expected Repository Contents

Every project generated or maintained within this workspace must include the following directory and file layout:

```text
├── README.md                          # Comprehensive project overview, AI workflow, and setup instructions
├── product-spec.md                    # Detailed functional & technical requirements specification
├── AGENTS.md                          # This master governance file and agent instructions
├── openapi.yaml                       # Strict OpenAPI 3.0+ API contract governing frontend & backend
├── docker-compose.yml                 # Multi-service container orchestration (frontend, backend, database)
├── .github/workflows/                 # Automated CI/CD pipeline definitions
│   └── ci-cd.yml                      # Automated linting, testing, and deployment pipeline
├── frontend/                          # Functional, well-structured frontend application with unit tests
├── backend/                           # API-contract-compliant backend service with unit tests
├── docs/                              # System documentation & architectural blueprints
│   ├── user-guide.md                  # Comprehensive frontend user guide & operational manual
│   ├── architecture.md                # System component interactions and data flow
│   ├── agent-extension-pack.md        # Agent capabilities, custom prompts, and workflows documentation
│   └── permissions.md                 # Security, tool execution, and environment permission boundaries
├── security/                          # Security audits, deterministic scans, and AI tool/data policy
│   ├── security-audit.md              # Static security analysis and vulnerability mitigations
│   └── ai-data-policy.md              # AI governance, data privacy, and tool usage policy
├── ops/                               # Operational diagnosis, health monitoring, and logging runbooks
│   ├── runbook.md                     # Incident handling and operational diagnosis guide
│   └── health-check.sh                # Operational verification script
├── agent-capabilities/                # Custom skills, specialized personas, and reusable prompt sequences
├── agent-hooks/                       # Execution hooks, pre-commit checks, and safety guardrails
├── mcp-server/                        # Model Context Protocol (MCP) tool and resource server implementation
└── plugins/                           # Custom agent extensions and workflow plugins
```

---

## Part B: Peer Review Evaluation Rubric & Quality Criteria

The project must be structured to achieve the highest possible score across all **14 peer-review criteria**:

### 1. Problem Description (Target: 2/2 points)
- **Standard**: The `README.md` and `product-spec.md` must clearly articulate the core problem, user personas, end-to-end system functionality, expected inputs/outputs, and behavioral edge cases.
- **Artifacts**: [README.md](file:///home/deai/zoomcamp/myprojects/aidevtools/README.md), [product-spec.md](file:///home/deai/zoomcamp/myprojects/aidevtools/product-spec.md).

### 2. AI-Assisted Development Workflow (Target: 2/2 points)
- **Standard**: Clear and explicit documentation in `README.md` detailing how AI tools (e.g., Antigravity, AGY CLI) were utilized throughout the lifecycle.
- **Required Details**: Specific prompt strategies, role-based agent delegation (`@pm`, `@engineer`, `@qa`, `@devops`), context file injection (`agents.md`, `skills/`), human-in-the-loop approval gates, manual code reviews, and verification steps.

### 3. Technologies and System Architecture (Target: 2/2 points)
- **Standard**: Explicitly document frontend, backend, database, containerization, and CI/CD tools, explaining the architectural rationale and how components interact.
- **Artifacts**: Visual architecture diagram (Mermaid/ASCII) and data flow descriptions in `README.md` and `docs/architecture.md`.

### 4. Frontend Implementation (Target: 3/3 points)
- **Standard**: Located in `frontend/`. Must be functional, beautifully designed (following modern UI/UX principles), and well-structured with centralized backend communication (API client module).
- **Testing Requirement**: Includes unit and component tests covering core logic, with clear, deterministic commands in `frontend/README.md` to run them.

### 5. API Contract (Target: 2/2 points)
- **Standard**: Complete `openapi.yaml` specification located at the root.
- **Validation**: Accurately reflects all frontend needs and serves as the strict, single source of truth for backend endpoints, schemas, parameters, and error responses.

### 6. Backend Implementation (Target: 3/3 points)
- **Standard**: Located in `backend/`. Strictly follows `openapi.yaml`, featuring clean modular structure (routes, controllers, models, services).
- **Testing Requirement**: Includes automated tests (e.g., `pytest` / unit test suites) verifying endpoints, request validation, and error states.

### 7. Database Integration (Target: 2/2 points)
- **Standard**: Proper persistent database layer (e.g., SQLite, PostgreSQL) with ORM/schema definitions, migrations/initialization scripts, and configuration for different environments (local development, testing, production).

### 8. Containerization (Target: 2/2 points)
- **Standard**: Root `docker-compose.yml` orchestrating all services (frontend, backend, database) with zero manual intervention.
- **Requirement**: `Dockerfile` in both `frontend/` and `backend/`, plus one-command boot instructions (`docker compose up --build`).

### 9. Integration Testing (Target: 2/2 points)
- **Standard**: Integration test suite clearly separated from unit tests (e.g., under `tests/integration/` or `backend/tests/integration/`).
- **Scope**: Tests realistic end-to-end workflows (e.g., client handshake $\to$ message dispatch $\to$ database persistence $\to$ response).

### 10. Deployment (Target: 2/2 points)
- **Standard**: Automated deployment scripts and documentation for hosting on cloud infrastructure (e.g., Google Cloud Run, Render, or Railway) with live working URLs or step-by-step reproducible deployment proof.

### 11. CI/CD Pipeline (Target: 2/2 points)
- **Standard**: Configured `.github/workflows/ci-cd.yml` that automatically triggers on pushes and pull requests to:
  1. Install dependencies and run linters.
  2. Execute unit and integration tests across frontend and backend.
  3. Build container images and trigger automated deployment when tests pass.

### 12. Agent Extension Pack (Target: 2/2 points)
- **Standard**: The repository must contain a complete, documented agent extension ecosystem:
  - `agent-capabilities/`: Custom reusable skills, agent profiles, and prompt instructions.
  - `agent-hooks/`: Hook scripts or safety guardrails for deterministic task execution.
  - `mcp-server/`: Model Context Protocol (MCP) server exposing tools/resources to coding agents.
  - `plugins/` or `custom-agent/`: Packaged modular agent extensions.
  - `docs/agent-extension-pack.md`: Architectural documentation describing each extension component.
  - `docs/permissions.md`: Explicit boundary notes declaring tool permissions, environment variables, and filesystem safety constraints.

### 13. Security, Audit, and DevOps Hardening (Target: 2/2 points)
- **Standard**: Dedicated `security/` and `ops/` directories containing:
  - Deterministic security scan outputs (e.g., dependency vulnerability audits, bandit/npm audit results).
  - Pull request (PR) audit report and checklist.
  - Operational diagnosis output and health monitoring runbook.
  - AI Tool & Data Governance Policy (`security/ai-data-policy.md`).

### 14. Reproducibility (Target: 2/2 points)
- **Standard**: Comprehensive, unambiguous instructions in `README.md` allowing any peer reviewer on Linux, macOS, or Windows to clone, configure (`.env.example`), test, and run the entire system in under 5 minutes without debugging missing dependencies.

---

## Part C: Agent Team Execution Matrix

| Agent Persona | Trigger Command / Skill | Primary Rubric Responsibilities |
| :--- | :--- | :--- |
| **@pm (Product Manager)** | `write_specs.md` | Criteria 1, 3, 5 (`product-spec.md`, `openapi.yaml`, Architecture blueprints) |
| **@engineer (Full-Stack)** | `generate_code.md` | Criteria 4, 6, 7 (`frontend/`, `backend/`, Database layer, Unit tests) |
| **@qa (QA & Security)** | `audit_code.md` | Criteria 9, 13 (Integration tests, `security/`, vulnerability audits) |
| **@devops (DevOps Master)** | `deploy_app.md` | Criteria 8, 10, 11, 14 (`docker-compose.yml`, CI/CD, deployment, `ops/`, `README.md`) |
| **@specialist (Agent Ops)**| `extend_agent.md` | Criteria 12 (`agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `docs/`) |
