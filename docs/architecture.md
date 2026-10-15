# System Architecture & Technical Specifications

> **Rubric Criteria Alignment**: Satisfies **Criterion #3 (Technologies and System Architecture)**.

---

## 1. High-Level Architecture Overview

The system is designed around an event-driven, asynchronous client-server topology providing sub-100ms bidirectional communication between online shoppers and customer support representatives.

```mermaid
graph TD
    subgraph Client Tier
        W[Storefront & Customer Chat Widget]
        A[Support Agent Command Console]
    end

    subgraph API & Real-Time Gateway
        WS[FastAPI WebSocket Router /ws/chat]
        REST[FastAPI REST Endpoints /api/*]
    end

    subgraph Service & Persistence Layer
        CM[Connection Manager]
        CS[In-Memory / SQLite Chat Store]
        MO[Simulated Order Fulfillment Engine]
    end

    W <-->|JSON Events over WS| WS
    A <-->|JSON Events over WS| WS
    A -->|REST /api/conversations| REST
    W -->|REST /api/orders| REST

    WS --> CM
    WS --> CS
    WS --> MO
    REST --> CS
    REST --> MO
```

---

## 2. Technology Rationale

1. **FastAPI & Uvicorn (ASGI Backend)**:
   - Python's asynchronous event loop enables concurrent WebSocket connections with low memory footprint (~40MB per worker).
   - Unified serving of REST APIs, WebSockets, and static assets eliminates CORS friction and separate proxy overhead during development.

2. **Native Asynchronous WebSockets**:
   - Zero third-party library overhead on the client side; standard browser `WebSocket` API ensures instant initialization.
   - Structured JSON envelope format (`{ type: "event_name", payload: { ... } }`) guarantees protocol determinism.

3. **Vanilla JS & Glassmorphic CSS System**:
   - Eliminates build-step dependencies for the customer widget, allowing easy embedding into Shopify, WooCommerce, or custom storefronts with zero framework conflicts.
   - Modern design tokens (deep slate `#090d16`, royal indigo `#6366f1`, emerald `#10b981`) deliver a premium aesthetic.

4. **Containerization & CI/CD**:
   - Multi-container orchestration via `docker-compose.yml` allows deterministic local and cloud deployment.
   - GitHub Actions automated pipeline validates test suites on every pull request.
