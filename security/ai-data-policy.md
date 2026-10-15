# AI Tool Governance & Data Privacy Policy

> **Rubric Criteria Alignment**: Satisfies **Criterion #13 (AI Tool and Data Policy)**.

---

## 1. Purpose & Scope

This policy governs the responsible use of Artificial Intelligence (AI) tools, Large Language Models (LLMs), and autonomous agent frameworks during development and operational deployment.

---

## 2. Core Policies

1. **Zero Customer PII Exposure**:
   - Customer messages and order lookup requests must never be transmitted to external, unvetted third-party AI models without explicit customer consent and sanitization.
   - All customer support chat logs generated in development and testing utilize synthetic mock customer personas (e.g. Alex Morgan, Sophia Bennett) and fictional order numbers.

2. **Model Transparency & Attribution**:
   - Automated agent responses in the chat system are clearly designated with system badges and automated assistant labels (`Support Bot`, `Order Assistant`) so shoppers always know when they are interacting with an automated agent versus a human specialist.

3. **Code Quality & Human Verification**:
   - All code synthesized by AI developer pipelines (`@engineer`, `@pm`) must pass human approval gates and automated test suites before deployment into production.
   - Autonomous agents are governed by deterministic guardrail hooks to prevent accidental destructive operations.
