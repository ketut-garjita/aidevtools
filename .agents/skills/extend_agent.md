# Skill: Extend Agent (Agent Ops Specialist)

## Objective
Your goal as the Agent Ops Specialist (@specialist) is to package and document the complete agent extension ecosystem, satisfying Rubric Criterion #12 (Agent Extension Pack).

## Rules of Engagement
- **Standard**: Follow the requirements in root [AGENTS.md](file:///home/deai/zoomcamp/myprojects/aidevtools/AGENTS.md).
- **Target Directories**:
  - `agent-capabilities/`: Specialized agent personas, reusable workflows, and task prompts.
  - `agent-hooks/`: Pre/post tool execution hooks, validation guardrails, and deterministic checks.
  - `mcp-server/`: Model Context Protocol (MCP) server implementation with custom tools.
  - `plugins/`: Modular, installable agent extensions.
  - `docs/agent-extension-pack.md`: Architecture overview of capabilities, hooks, and MCP tools.
  - `docs/permissions.md`: Explicit permission boundaries, environment variables, and safety rules.

## Instructions
1. Scaffold `mcp-server/` with a working server script (e.g. `server.py` or `index.js`) exposing project-specific tools (e.g., order querying, system health inspection, database maintenance).
2. Create `agent-capabilities/` with prompt templates and capability descriptors.
3. Create `agent-hooks/` with guardrail scripts (e.g., pre-commit file check, API schema validator).
4. Draft comprehensive documentation in `docs/agent-extension-pack.md` and `docs/permissions.md`.
