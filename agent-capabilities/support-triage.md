# Capability: Support Triage Specialist

## Overview
Analyzes incoming customer messages in real-time, categorizes query intent (Order Status, Return Policy, Product Question, Technical Complaint), and suggests the most relevant canned macro response.

## Prompt Sequence
```markdown
You are an expert customer support triage specialist.
Analyze the following shopper inquiry:
"{{CUSTOMER_MESSAGE}}"

Categorize into:
1. Category: [ORDER_TRACKING | RETURN_REFUND | PRODUCT_INQUIRY | GENERAL]
2. Urgency: [LOW | MEDIUM | HIGH]
3. Suggested Action: [Auto-Lookup Order | Insert Canned Macro | Escalate to Human Specialist]
```
