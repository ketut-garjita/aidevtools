---
description: Start the Autonomous AI Developer Pipeline sequence with a new idea
---

When the user types `/startcycle <idea>`, orchestrate the development process strictly following `AGENTS.md`, `.agents/agents.md`, and `.agents/skills/` to fulfill all 14 peer review rubric criteria.

### Execution Sequence:
1. Act as the **Product Manager (@pm)** and execute the `write_specs.md` skill using the `<idea>`.
   *(Generate `product-spec.md`, `openapi.yaml`, and `docs/architecture.md`. Wait for the user to explicitly approve the spec. If the user provides feedback or adds comments, revise and loop until they type "Approved").*
2. Shift context, act as the **Full-Stack Engineer (@engineer)**, and execute the `generate_code.md` skill.
   *(Generate `frontend/` with tests, `backend/` with tests, and database layer adhering to `openapi.yaml`).*
3. Shift context, act as the **QA & Security Auditor (@qa)**, and execute the `audit_code.md` skill.
   *(Create integration tests under `tests/integration/`, perform security audits, and generate `security/` & `ops/` artifacts).*
4. Shift context, act as the **DevOps Master (@devops)**, and execute the `deploy_app.md` skill.
   *(Generate `docker-compose.yml`, `.github/workflows/ci-cd.yml`, `README.md`, and host locally or cloud).*
5. Shift context, act as the **Agent Ops Specialist (@specialist)**, and execute the `extend_agent.md` skill.
   *(Generate `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `plugins/`, `docs/agent-extension-pack.md`, and `docs/permissions.md`).*