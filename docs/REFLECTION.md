# Reflection: Where the Agent Adds Value

## Where the agent genuinely adds value

The strongest value is not simply producing more test cases. A human tester can manually write many of these cases quickly. The useful part is the **self-checking loop**.

### 1. It makes omissions visible

A human may read acceptance criteria and mentally cover most of them, but the agent maintains an explicit AC-to-test mapping. Missing coverage becomes a machine-detectable gap.

### 2. It systematically asks for different test perspectives

The critic checks positive, negative, boundary and edge categories. This is particularly useful for lockout thresholds, session expiry, minimum promo thresholds, discount caps and cart changes after a promo is applied.

### 3. It turns review into an executable step

Instead of saying “I think the tests cover the requirements,” the agent produces a coverage report. The same logic can be rerun whenever requirements change.

### 4. It creates a repeatable workflow

The input → generation → critique → repair → export flow is reusable. For a large backlog of user stories, this reduces repetitive test-design work.

## Where manual test writing would suffice

For a small, stable feature such as the supplied examples, an experienced QA engineer could manually create a high-quality suite quickly. Human reasoning is also better when requirements are ambiguous, domain-specific or dependent on undocumented system behavior.

The agent should therefore be treated as an accelerator and reviewer, not as a replacement for QA judgment.

## What I would improve next

1. Add an LLM-backed generator for natural-language requirements.
2. Keep the critic deterministic where possible, because machine-checkable coverage is more reliable than asking an LLM whether its own output is complete.
3. Add semantic duplicate detection.
4. Add configurable import mappings for TestRail and Zephyr.
5. Add a small web UI for uploading a user story and downloading the suite.
6. Add risk scoring based on business impact, likelihood and detectability.
7. Add mutation tests: deliberately remove a case and verify the critic detects the gap.

## Bottom line

The agent's genuine contribution is the **generate-then-critique feedback loop**. It changes test generation from a one-shot writing task into an iterative coverage process. Manual expertise remains essential for interpreting ambiguous requirements and validating that generated tests make sense in the actual product.
