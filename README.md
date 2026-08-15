# Test Case Generator Agent

An offline, deterministic agent that converts user stories + acceptance criteria into a requirement-traceable test suite.

## What makes it agentic

The implementation deliberately uses a **generate → critique → repair** loop rather than a single generation call:

1. **Generate** an initial set of positive and negative cases.
2. **Critique** the draft against every acceptance criterion and required category.
3. **Repair** the suite by generating missing cases for each detected coverage gap.
4. Repeat until the critique reports no gaps or the configured iteration limit is reached.

The orchestration is independent of the generation strategy, so a future LLM adapter can replace the deterministic rule engine.

## Features

- Feature A: User Login
- Feature B: Apply Promo Code at Checkout
- Requirement traceability to AC IDs
- Categories: positive / negative / boundary / edge
- Risk-based priorities: P0 / P1 / P2 / P3
- CSV suitable for import/mapping to TestRail/Zephyr
- Gherkin/BDD output
- Explicit coverage-gap reports
- Automated tests for the agent loop

## Run

```bash
python agent.py
```

Outputs are written to `outputs/`.

Run tests:

```bash
python -m unittest discover -s tests
```

or, if pytest is installed:

```bash
pytest
```

## Repository layout

```text
test-case-generator/
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
    └── REFLECTION.md
```

## Demo

For a 10-minute evaluator demo:

1. Show Feature A and Feature B input specs.
2. Run `python agent.py`.
3. Open `outputs/all_test_cases.csv`.
4. Filter by `acceptance_criteria`, `category`, and `priority`.
5. Open the coverage report and show that the critique loop found and repaired gaps.
6. Change one acceptance criterion or add a new rule, rerun, and show the generated repair case.
7. Show the Gherkin output.

## Limitations / next step

This submission is intentionally offline and deterministic so it is reproducible without credentials. For production use, the generator can be replaced with an LLM provider while retaining the same agent state, critique contract, traceability checks, and export layer.
