# Test Case Generator Agent

An offline, deterministic **requirement-driven test-case generation agent**. It reads user stories, descriptions, acceptance criteria and explicit feature rules, then produces a categorized, risk-prioritized and requirement-traceable suite.

## What makes it agentic

The implementation deliberately uses a real **generate → critique → repair** loop:

1. **Generate** an initial positive/negative draft.
2. **Critique** the draft against every acceptance criterion, required category, explicit business rule and quoted error message.
3. **Repair** concrete gaps with requirement-specific boundary/edge/state/message cases.
4. Re-run the critic until no gaps remain or the iteration limit is reached.

For the supplied requirements the final run produces **36 User Login cases + 48 Promo Code cases = 84 cases**, with two iterations per feature and zero final coverage gaps.

## Features

- Feature A: User Login
- Feature B: Apply Promo Code at Checkout
- Requirement traceability to AC IDs
- Explicit business-rule traceability
- Categories: positive / negative / boundary / edge
- Risk-based priorities: P0 / P1 / P2 / P3
- Exact required-message assertions
- CSV suitable for TestRail/Zephyr mapping
- Gherkin/BDD output
- Machine-readable coverage-gap reports
- Automated tests for generation, critique, repair and exports
- No external API key required

## Run

```bash
python agent.py
```

Outputs are written to `outputs/`.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Generated artifacts

- `outputs/all_test_cases.csv`
- `outputs/test_cases_A.csv`
- `outputs/test_cases_B.csv`
- `outputs/test_suite_A.feature`
- `outputs/test_suite_B.feature`
- `outputs/coverage_report_A.json`
- `outputs/coverage_report_B.json`
- `outputs/coverage_summary.json`

Each CSV test case includes feature, category, priority, acceptance criterion, rule trace, preconditions, steps, expected result and risk.

## Repository layout

```text
├── agent.py
├── requirements.txt
├── README.md
├── specs/
│   ├── feature_a.json
│   └── feature_b.json
├── outputs/
├── tests/
│   └── test_agent.py
└── docs/
    ├── DESIGN.md
    ├── REFLECTION.md
    └── REFLECTION.pdf
```

## Demo

For a 10-minute evaluator demo:

1. Show the two input specifications.
2. Run `python agent.py`.
3. Show that iteration 1 contains coverage gaps.
4. Show iteration 2 after targeted repairs.
5. Open `outputs/all_test_cases.csv` and filter by AC/category/priority.
6. Open the coverage reports and show zero final gaps, including business rules and exact messages.
7. Open the Gherkin suite.
8. Run `python -m unittest discover -s tests -v`.

## Design decision

The core engine is deterministic and offline so the capstone is reproducible without credentials or network access. The orchestration and structured output contract are intentionally separated from the generator, so an LLM-backed generator can be added later without replacing the critic, traceability or export layers.
