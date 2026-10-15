# Agent Execution Permissions & Safety Boundaries

> **Rubric Criteria Alignment**: Satisfies **Criterion #12 (Agent Extension Pack - Permission Notes)**.

---

## 1. Security & Principle of Least Privilege

Autonomous AI agents operating on this repository adhere to the principle of least privilege. Explicit boundaries are established for tool execution, network access, and filesystem modifications.

---

## 2. Permission Matrix

| Capability / Action | Permission Level | Guardrail & Boundary |
| :--- | :--- | :--- |
| **Filesystem Read** | Full Workspace | Restricted to workspace directory (`/home/deai/zoomcamp/myprojects/aidevtools`). |
| **Filesystem Write** | Workspace Only | Permitted only within `app_build/`, `frontend/`, `backend/`, `docs/`, `security/`, `ops/`. Modifying system files outside workspace is blocked. |
| **Command Execution** | Sandboxed Local | Permitted for testing, package installation (`pip`, `npm`), and local server runners. Destructive commands (`rm -rf /`, privileged sudo operations) are explicitly forbidden. |
| **Network / Web Access** | Restricted | Outbound requests permitted for package registries (`PyPI`, `npm`) and local port binding (`localhost:8000`). |
| **Secrets & Credentials** | Prohibited | Agents must never output, hardcode, or log API keys or passwords. Environment variables are loaded via `.env` templates only. |

---

## 3. Environment Variable Boundaries

| Variable Name | Default Value | Required Scope | Sensitivity |
| :--- | :--- | :--- | :--- |
| `PORT` | `8000` | Local Server Binding | Public / Non-sensitive |
| `ENV` | `development` | Runtime environment mode | Public / Non-sensitive |
| `DATABASE_URL` | `sqlite:///chat.db` | Storage connection | Internal |
