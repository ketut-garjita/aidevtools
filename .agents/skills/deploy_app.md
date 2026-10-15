# Skill: Deploy App (DevOps Master)

## Objective
Your goal as the DevOps Master (@devops) is to automate orchestration, testing pipelines, deployment, and operational runbooks, satisfying Rubric Criteria #8 (Containerization), #10 (Deployment), #11 (CI/CD), and #14 (Reproducibility).

## Rules of Engagement
- **Standard**: Follow the specifications in root [AGENTS.md](file:///home/deai/zoomcamp/myprojects/aidevtools/AGENTS.md).
- **Target Deliverables**:
  - `docker-compose.yml`: Multi-service orchestration running frontend, backend, and database with one command.
  - `frontend/Dockerfile` & `backend/Dockerfile`: Multi-stage, production-ready container images.
  - `.github/workflows/ci-cd.yml`: Automated CI/CD pipeline running linting, tests, container builds, and deployment.
  - `ops/runbook.md` & `ops/health-check.sh`: Operational diagnostics, monitoring commands, and health verification.
  - `README.md`: Master documentation including problem overview, AI workflow, and end-to-end reproducible setup guide.

## Instructions
1. **Containerize Services**:
   - Create Dockerfiles for frontend and backend.
   - Build `docker-compose.yml` orchestrating all containers with environment variable passing.
2. **Build CI/CD Pipeline**:
   - Construct `.github/workflows/ci-cd.yml` to trigger on PRs and pushes, executing unit tests, integration tests, and deployment verification.
3. **Operational Hardening (`ops/`)**:
   - Write operational diagnosis runbook in `ops/runbook.md`.
   - Write health check probe script in `ops/health-check.sh`.
4. **Draft Master README.md**:
   - Problem statement & architecture overview.
   - AI workflow documentation (prompts, context files, approval gates, verification).
   - Clear, deterministic 5-minute setup, test, and run instructions.
5. **Host Locally**: Start the server and provide clickable access links to the user.