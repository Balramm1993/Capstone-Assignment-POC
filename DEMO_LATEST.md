# Latest Evaluator Demo Checklist

This file is a visible marker for the latest evaluator-ready repository update.

## 10-minute demo

1. Run `python demo.py` (or `py demo.py` on Windows).
2. Choose `2` and show Generate -> Critique -> Repair.
3. Choose `3` for Login `AC6` and show lockout boundary/state cases.
4. Choose `3` for Promo `AC3` or `AC8` and show threshold/cap cases.
5. Choose `4` and ask: `What coverage gaps remain for login?`
6. Open `outputs/all_test_cases.csv` and show AC traceability, category and priority.
7. Open the coverage reports and explain acceptance-criteria and business-rule coverage.
8. Run `python -m unittest discover -s tests -v` (or `py -m unittest discover -s tests -v`).

## High-value scenarios to demonstrate

### Feature A — Login
- Password: 7, 8, 64 and 65 character boundaries.
- Empty-field validation must result in no authentication request.
- Lockout: 4 failures vs 5 failures, 15-minute window, 30-minute lock duration.
- Session: 23:59:59 vs 24:00:00 expiry and post-logout access.
- Email case-insensitivity vs password case-sensitivity.

### Feature B — Promo
- Single-use code is enforced per customer.
- Discount cap: subtotal ₹150, ₹200 and ₹201.
- Minimum-order threshold below/equal/above the threshold.
- Replacement confirmation: confirm applies only the new code; cancel preserves the old code.
- Shipping and tax use the discounted subtotal.
- Cart changes trigger promo re-validation when eligibility changes.

## Evaluator message

The key value is not simply producing many test cases. The agent generates a draft, critiques it against acceptance criteria and explicit business rules, repairs concrete gaps, and re-checks coverage before exporting the final traceable suite.
