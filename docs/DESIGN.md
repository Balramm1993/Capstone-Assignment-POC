# Design Writeup

## Problem

Given a user story, acceptance criteria and explicit business rules, generate a categorized, requirement-traceable test suite for both supplied features. The suite must include positive, negative, boundary and edge coverage, risk prioritization, importable output and an explicit coverage-gap report.

## Architecture

```text
Feature JSON
   ↓
Requirement parser
   ↓
Draft test generator
   ↓
Coverage critic
   ├── acceptance-criteria coverage
   ├── category coverage
   ├── required-message coverage
   └── explicit business-rule coverage
   ↓
Targeted repair
   ↓
Re-critique
   ↓
CSV + Gherkin + coverage reports
```

The implementation is deterministic and does not require an external API key. This makes the demo reproducible in a clean CI environment. The generation layer is isolated so an LLM adapter could be added later without changing the traceability/export pipeline.

## Generate → Critique → Repair

The first pass intentionally creates a smaller draft. The critic checks each acceptance criterion and identifies missing meaningful categories, required messages and explicit rules. The repair stage adds requirement-specific scenarios rather than generic filler. The repaired suite is critiqued again until the gap list is empty or the configured iteration limit is reached.

This is the core agentic behavior required by the assignment: the final suite is the result of iterative self-checking, not a single-shot list.

## Semantic coverage examples

### Login

The suite explicitly covers password boundaries of **7 / 8 / 64 / 65** characters, blank-field request suppression, email-format partitions, the **4 vs 5** lockout threshold, the **15-minute** qualifying window, the **30-minute** lock duration, email/password case sensitivity, the **23:59:59 / 24:00:00** session boundary, logout invalidation and inactive-account access control.

### Promo

The suite explicitly covers percentage calculations, fixed-code minimum **₹999 / ₹1000 / ₹1001**, expiry timing, invalid codes, case normalization, single-use **per customer**, replacement confirmation/cancellation, the discount-cap **₹150 / ₹200 / ₹201** boundaries, shipping/tax calculation from the discounted subtotal, whitespace handling and cart revalidation at **₹1000 / ₹999**.

## Traceability and risk

Every generated test contains:

- acceptance criterion ID
- business-rule trace where applicable
- category
- risk priority
- preconditions
- steps
- expected result

High-impact authentication and pricing/security scenarios receive P0/P1 priorities.

## Outputs

The agent exports:

- CSV test suites
- Gherkin/BDD feature files
- coverage JSON
- coverage-gap Markdown reports

## Testing strategy

The regression suite checks final zero-gap status, category coverage, exact required messages, business-rule coverage, concrete boundary scenarios, generate/critique/repair iteration behavior and importable traceable output.

## What broke and how it was fixed

During development the project encountered path/import issues and an interactive-demo indentation problem. The test suite now inserts the repository root into `sys.path`, and the CLI loader was corrected so the demo starts cleanly. Regression tests were strengthened so future changes cannot silently remove the important boundary and business-rule scenarios.
