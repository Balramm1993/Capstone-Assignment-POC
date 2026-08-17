# Reflection

## Where the agent genuinely added value

The agent is most useful when a requirement contains interacting rules and boundary conditions. Manually writing a few happy-path tests is easy; systematically checking all acceptance criteria, explicit business rules, error messages, thresholds and state transitions is where the iterative critic adds value.

For login, the agent made the lockout rule concrete by testing 4 vs 5 failures, the 15-minute qualifying window, the 30-minute lock period and correct credentials during an active lock. It also makes the password constraint explicit with 7/8/64/65-character cases and checks that empty-field validation suppresses the authentication request.

For promo codes, the agent catches interactions that are easy to overlook manually: single-use being per customer, replacement requiring confirmation, the fixed-discount cap at ₹150/₹200/₹201, shipping and tax being based on the discounted subtotal, and revalidation when a cart change crosses the ₹1000 minimum threshold.

## Where manual testing would have sufficed

For very small features with one or two simple acceptance criteria, manually writing a handful of tests would be faster than running the agent. The agent's overhead is justified when the requirement set is larger, changes frequently, or contains many business rules and thresholds.

## What the critique loop adds

A single-shot generator can produce plausible cases while still missing a requirement. The critic forces an explicit coverage check and the repair phase generates additional targeted scenarios. The final output is therefore auditable: a reviewer can trace a test to an acceptance criterion and, where applicable, to a business rule.

## Limitations

This submission uses deterministic rules for reproducibility and does not claim to be a general-purpose LLM chatbot. The architecture can be extended with an LLM adapter, richer domain-specific reasoning, and direct TestRail/Zephyr/Jira integrations.
