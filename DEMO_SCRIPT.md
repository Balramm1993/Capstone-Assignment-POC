# 10-Minute Evaluator Demo Script

## 0:00–1:00 — Introduce the solution

> This project is a requirement-driven test-case generation agent. It reads the user story, acceptance criteria and business rules, generates categorized and traceable tests, critiques the draft for coverage gaps, repairs the gaps, and exports CSV and Gherkin suites.

## 1:00–2:30 — Explain the agentic loop

Show the flow:

```text
Requirement
   ↓
Draft generation
   ↓
Coverage critic
   ↓
Gap detection
   ↓
Targeted repair
   ↓
Re-critique
   ↓
Final suite
```

Run:

```bash
py demo.py
```

Choose **2** and select **A**. Explain that the first iteration is intentionally incomplete and the repair stage adds concrete missing scenarios.

## 2:30–5:00 — Login feature

Choose **3**, Feature A, **AC6**, category `boundary`.

Highlight:
- 4 failures vs 5 failures
- 15-minute qualifying window
- 30-minute lock period
- correct credentials do not bypass an active lock

Then show AC1 and explain the password constraint:
- 7 characters — below minimum
- 8 — minimum boundary
- 64 — maximum boundary
- 65 — above maximum

Mention AC4 explicitly: the test verifies that no authentication request is sent for blank required fields.

## 5:00–7:30 — Promo feature

Choose **3**, Feature B, **AC8**, category `boundary`.

Highlight:
- ₹150 → ₹0
- ₹200 → ₹0
- ₹201 → ₹1

Then show AC7 and explain that single-use is **per customer**, not globally. Customer A cannot reuse a redeemed code, while Customer B may use it if otherwise eligible.

Show AC9 to demonstrate confirm/cancel replacement behavior and no stacking.

Show AC12 to demonstrate revalidation after cart changes at ₹1000/₹999.

## 7:30–8:30 — Outputs

Show `outputs/` and explain:
- CSV is importable into test-management tooling.
- Gherkin is BDD-ready.
- Coverage reports show AC/category/business-rule coverage.
- Each test carries acceptance-criteria and rule traceability plus risk priority.

## 8:30–10:00 — Evaluator questions

### Why is it agentic?

> It is iterative: generation is followed by critique, gap detection, targeted repair and re-critique. The final suite is not simply the first generated draft.

### Why not write the tests manually?

> Manual testing is fine for small requirements. The agent adds value by systematically checking a larger set of acceptance criteria, explicit rules and boundary conditions and by regenerating missing coverage when the requirement changes.

### Is it a generic LLM chatbot?

> No. This submission deliberately uses deterministic, reproducible requirement-to-test logic so the demo works without an API key. The orchestration is designed so a future LLM adapter can replace or augment the deterministic generation layer.

### What are the limitations?

> The current assignment implementation is optimized for the supplied feature specifications. A production version would add richer domain inference, configurable test-management integrations and an LLM-backed reasoning adapter.
