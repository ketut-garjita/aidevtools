# Skill: Generate Code (Full-Stack Engineer)

## Objective
Your goal as the Full-Stack Engineer (@engineer) is to implement the application based on the approved `product-spec.md` and `openapi.yaml`, satisfying Rubric Criteria #4 (Frontend Implementation), #6 (Backend Implementation), and #7 (Database Integration).

## Rules of Engagement
- **Standard**: Follow the specifications in root [AGENTS.md](file:///home/deai/zoomcamp/myprojects/aidevtools/AGENTS.md).
- **Target Directories**:
  - `frontend/`: Clean, modular frontend codebase with centralized API communication client, responsive modern UI, and automated unit/component tests.
  - `backend/`: Clean, modular backend codebase strictly implementing `openapi.yaml`, with automated endpoint unit tests.
  - Database layer: Properly integrated persistent storage supporting local, test, and production environments.

## Instructions
1. **Study Contracts**: Review `product-spec.md` and `openapi.yaml`. Ensure every endpoint and schema is mapped to a backend route and frontend client method.
2. **Scaffold Frontend (`frontend/`)**:
   - Centralized API/WebSocket client module.
   - High-aesthetic, responsive, accessible components.
   - Frontend unit test suite and run instructions in `frontend/README.md`.
3. **Scaffold Backend (`backend/`)**:
   - Structured routes, controllers, services, and models.
   - Input validation conforming to `openapi.yaml`.
   - Backend unit test suite (e.g., `pytest`).
4. **Database Integration**:
   - Integrate persistent database layer with schema migrations / initialization scripts.
5. **No Shortcuts**: Do not use placeholder code or skipped logic blocks.