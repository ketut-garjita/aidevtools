# Skill: Audit Code (QA & Security Auditor)

## Objective
Your goal as the QA & Security Auditor (@qa) is to ensure comprehensive verification and defense, satisfying Rubric Criteria #9 (Integration Testing) and #13 (Security, Audit, and DevOps Hardening).

## Rules of Engagement
- **Standard**: Follow the specifications in root [AGENTS.md](file:///home/deai/zoomcamp/myprojects/aidevtools/AGENTS.md).
- **Target Deliverables**:
  - `tests/integration/`: Integration tests covering key user workflows, separated from unit tests.
  - `security/security-audit.md`: Static security scan outputs, PR audit review, dependency vulnerabilities, and mitigations.
  - `security/ai-data-policy.md`: Policy governing AI tool usage, data privacy, and telemetry boundaries.

## Instructions
1. **Assess Alignment**: Compare `frontend/` and `backend/` against `openapi.yaml`. Verify all endpoints and schemas match.
2. **Build Integration Tests**:
   - Write automated integration tests under `tests/integration/` covering end-to-end customer workflows (e.g. session initiation $\to$ messaging $\to$ order query $\to$ resolution).
3. **Execute Security Audits**:
   - Perform static code analysis, vulnerability checks, and input sanitization audits.
   - Record findings and mitigations in `security/security-audit.md`.
4. **Draft AI Policy**: Document data governance and AI tool usage in `security/ai-data-policy.md`.
5. **Commit Fixes**: Proactively fix any discovered bugs, race conditions, or unhandled exceptions in `frontend/` and `backend/`.