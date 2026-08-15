# Design Writeup

## 1. Problem

The assignment requires an agent that reads a user story, acceptance criteria and feature rules, then produces a categorized, requirement-traceable suite. A useful solution must do more than generate many plausible cases: it must detect omissions and repair them.

The upgraded implementation therefore treats **coverage analysis as part of generation**, not as a post-hoc manual claim.

## 2. Architecture

```text
JSON requirement
      |
      v
Requirement parser
      |
      +--> user story / description
      +--> acceptance criteria
      +--> explicit rules / notes
      |
      v
Initial generator
      |  positive + negative draft
      v
Coverage critic
      |
      +--> AC/category gaps
      +--> explicit business-rule gaps
      +--> required-message gaps
      |
      v
Targeted repair generator
      |
      +--> boundary cases
      +--> edge/state/timing cases
      +--> exact-message assertions
      |
      +----> re-critique (until clean or max iterations)
      |
      v
CSV + Gherkin + JSON coverage reports
```

The initial generator intentionally starts with a smaller draft. This is important: the first iteration is allowed to have gaps, which demonstrates a genuine **generate -> critique -> repair** loop rather than a fake loop where the first draft is already complete.

## 3. Requirement-driven generation

Every test case contains:

- feature
- category: positive / negative / boundary / edge
- priority
- acceptance criterion ID
- rule trace
- title
- preconditions
- executable steps
- expected result
- risk
- source (initial generation, targeted rule repair, message repair, etc.)

The supplied login and promo requirements are used as input JSON, not as a hard-coded list of final test cases.

The generator uses the language of each acceptance criterion to select meaningful scenarios. Timing language produces lockout/session boundary cases; minimum/amount language produces threshold cases; case-insensitive language produces case permutations; replacement/cart-change language produces state-transition cases.

## 4. Critique design

The critic checks three layers:

### Acceptance-criterion coverage
Every AC must have all four assignment categories represented.

### Explicit rule coverage
For Feature B, every promo rule is checked independently. This prevents a suite from claiming AC coverage while silently missing a rule such as per-customer usage, discount caps, or discounted-subtotal tax calculation.

### Exact required messages
Quoted error messages in the requirements are extracted and checked against test expectations.

The coverage report therefore answers not only "is AC3 present?" but also "which categories, rules and exact messages are covered?"

## 5. Repair loop

When the critic finds a gap, the repair stage generates a **specific** case for that gap. It does not add generic filler such as "Boundary coverage for AC3". Examples include:

- Login: 4 vs 5 failed attempts and the 15-minute lockout window.
- Login: 23:59:59 vs 24:00 session expiry.
- Login: 7/8/64/65 character password boundaries.
- Promo: ₹999/₹1000/₹1001 minimum-order boundary.
- Promo: ₹150/₹200/₹201 discount-cap boundary.
- Promo: same customer reuse vs another customer.
- Promo: replacement confirmation/cancellation.
- Promo: cart changes that cross the eligibility threshold.

The loop stops when the critic reports zero gaps or when the configured iteration limit is reached.

## 6. Output design

The repository generates:

- `all_test_cases.csv` — combined import-friendly suite.
- `test_cases_A.csv` and `test_cases_B.csv` — feature-specific CSVs.
- `test_suite_A.feature` and `test_suite_B.feature` — Gherkin/BDD.
- `coverage_report_A.json` and `coverage_report_B.json` — detailed machine-readable evidence.
- `coverage_summary.json` — final run summary.

CSV columns include the AC ID and rule trace, making the suite directly suitable for mapping into TestRail/Zephyr import fields.

## 7. Risk-based prioritization

P0 is used for authentication, account security, pricing integrity, lockout, session, promo eligibility and other high-impact behaviors. P1 is used for important validation, normalization and secondary state behavior.

The priority is attached to every test case rather than being a separate report.

## 8. What broke and how it was fixed

### Generic filler cases
The first version used generic category templates. These could technically satisfy a category check while adding little testing value.

**Fix:** repair cases are now feature/rule specific, with concrete values, messages, state transitions and timing boundaries.

### Weak coverage model
The first critic only checked whether every AC had one case in each category.

**Fix:** the critic now checks AC/category coverage, explicit business rules and exact required messages.

### Password boundary omission
The original suite covered 8 and 64 characters but not 7 and 65.

**Fix:** the login suite now explicitly tests 7/8/64/65.

### Promo per-customer usage
The original suite checked reuse by the same customer but did not clearly prove the rule was per customer.

**Fix:** the suite now tests Customer A reuse and Customer B first use.

### Pytest/import discovery issue
The original tests could fail under standard test discovery because the repository root was not guaranteed to be importable.

**Fix:** the test module adds the repository root to `sys.path`, and the suite is runnable with `python -m unittest discover`.

## 9. Validation

The upgraded repository validates that both feature specifications reach zero final gaps, every AC has all four categories, required messages are asserted, promo rules are covered, the generate/critique/repair loop takes multiple iterations, and the CSV export remains requirement-traceable.

The current generated run contains **36 login cases + 48 promo cases = 84 cases**, with two iterations per feature and zero final coverage gaps.
