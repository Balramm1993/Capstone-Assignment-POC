Feature: Apply Promo Code at Checkout

  # B-TC-001 | positive | P0 | AC1 | AC1
  Scenario: AC1: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC1: Applying SAVE10 to a ₹1000 subtotal reduces it by ₹100; the order total updates accordingly.
    Then The system satisfies AC1 exactly, including the stated outcome and message/state.

  # B-TC-002 | negative | P0 | AC1 | AC1
  Scenario: Invalid percentage input does not apply discount
    Given Feature is available with required test data.
    When Alter the code or use an invalid percentage code and apply it.
    Then Invalid/ineligible code is rejected and the order total is unchanged.

  # B-TC-003 | positive | P0 | AC2 | AC2
  Scenario: AC2: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC2: Applying FLAT200 to a ₹1500 subtotal reduces it by ₹200.
    Then The system satisfies AC2 exactly, including the stated outcome and message/state.

  # B-TC-004 | negative | P0 | AC2 | AC2
  Scenario: Fixed code rejected when not eligible
    Given Feature is available with required test data.
    When Apply FLAT200 below its eligibility threshold.
    Then The code is rejected and the total remains unchanged.

  # B-TC-005 | positive | P0 | AC3 | AC3
  Scenario: AC3: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC3: Applying FLAT200 to an ₹800 subtotal is rejected with "This code requires a minimum order of ₹1000."
    Then The system satisfies AC3 exactly, including the stated outcome and message/state.

  # B-TC-006 | negative | P0 | AC3 | AC3
  Scenario: Fixed code below minimum shows exact message
    Given Feature is available with required test data.
    When Apply FLAT200 at ₹800.
    Then The exact 'This code requires a minimum order of ₹1000.' message is shown and the total is unchanged.

  # B-TC-007 | positive | P0 | AC4 | AC4
  Scenario: AC4: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC4: Applying an expired code shows "This code has expired." and the total is unchanged.
    Then The system satisfies AC4 exactly, including the stated outcome and message/state.

  # B-TC-008 | negative | P0 | AC4 | AC4
  Scenario: Expired code is rejected
    Given Feature is available with required test data.
    When Apply the expired code.
    Then The exact 'This code has expired.' message is shown and total is unchanged.

  # B-TC-009 | positive | P0 | AC5 | AC5
  Scenario: AC5: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC5: Applying a non-existent code shows "Invalid promo code." and the total is unchanged.
    Then The system satisfies AC5 exactly, including the stated outcome and message/state.

  # B-TC-010 | negative | P0 | AC5 | AC5
  Scenario: Non-existent promo code
    Given Feature is available with required test data.
    When Enter a code that does not exist and click Apply.
    Then The exact 'Invalid promo code.' message is shown and the total is unchanged.

  # B-TC-011 | positive | P0 | AC6 | AC6
  Scenario: AC6: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC6: save10 behaves identically to SAVE10.
    Then The system satisfies AC6 exactly, including the stated outcome and message/state.

  # B-TC-012 | negative | P0 | AC6 | AC6
  Scenario: Case-insensitive promo identity
    Given Feature is available with required test data.
    When Apply SAVE10, save10 and SaVe10 on equivalent orders.
    Then All case variants resolve to the same code and discount.

  # B-TC-013 | positive | P0 | AC7 | AC7
  Scenario: AC7: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC7: Reapplying a single-use code already redeemed by the customer shows "This code has already been used."
    Then The system satisfies AC7 exactly, including the stated outcome and message/state.

  # B-TC-014 | negative | P0 | AC7 | AC7
  Scenario: Same customer cannot reuse single-use code
    Given Feature is available with required test data.
    When Customer A has already redeemed a single-use code; apply it again.
    Then The exact 'This code has already been used.' message is shown and no second discount is applied.

  # B-TC-015 | positive | P0 | AC8 | AC8
  Scenario: AC8: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC8: Applying FLAT200 to a ₹150 subtotal (where minimum is not required) results in a subtotal of ₹0, never negative.
    Then The system satisfies AC8 exactly, including the stated outcome and message/state.

  # B-TC-016 | negative | P0 | AC8 | AC8
  Scenario: Fixed discount never creates negative subtotal
    Given Feature is available with required test data.
    When Apply FLAT200 to subtotal ₹150.
    Then Discounted subtotal is exactly ₹0 and never becomes negative.

  # B-TC-017 | positive | P0 | AC9 | AC9
  Scenario: AC9: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC9: Applying a second code prompts the user to replace the first; on confirm, only the new discount applies.
    Then The system satisfies AC9 exactly, including the stated outcome and message/state.

  # B-TC-018 | negative | P0 | AC9 | AC9
  Scenario: Canceling replacement keeps first code
    Given Feature is available with required test data.
    When Apply a second code, then cancel the replacement prompt.
    Then First code and its discount remain active; second code is not applied.

  # B-TC-019 | positive | P0 | AC10 | AC10
  Scenario: AC10: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC10: Clicking Apply with no code shows "Enter a promo code."
    Then The system satisfies AC10 exactly, including the stated outcome and message/state.

  # B-TC-020 | negative | P0 | AC10 | AC10
  Scenario: Empty promo input
    Given Feature is available with required test data.
    When Leave Promo code blank and click Apply.
    Then The exact 'Enter a promo code.' message is shown and the order total is unchanged.

  # B-TC-021 | positive | P0 | AC11 | AC11
  Scenario: AC11: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC11: Leading/trailing spaces are trimmed before validation.
    Then The system satisfies AC11 exactly, including the stated outcome and message/state.

  # B-TC-022 | negative | P0 | AC11 | AC11
  Scenario: Whitespace is normalized before validation
    Given Feature is available with required test data.
    When Apply ' SAVE10 ', 'SAVE10 ', and ' SAVE10'.
    Then Each value is trimmed and resolves to SAVE10.

  # B-TC-023 | positive | P0 | AC12 | AC12
  Scenario: AC12: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC12: If the cart changes after a code is applied (e.g., an item is removed and subtotal drops below the minimum), the discount is re-validated and removed if no longer eligible.
    Then The system satisfies AC12 exactly, including the stated outcome and message/state.

  # B-TC-024 | negative | P0 | AC12 | AC12
  Scenario: Promo is removed after cart becomes ineligible
    Given Feature is available with required test data.
    When Apply FLAT200 at ₹1500, then remove items until subtotal is ₹800.
    Then The discount is revalidated, removed, and the order total is recalculated without FLAT200.

  # B-TC-025 | boundary | P0 | AC1 | AC1
  Scenario: Percentage discount calculation
    Given Feature is available with required test data.
    When Apply SAVE10 to subtotals ₹1, ₹1000 and ₹1500.
    Then Discount equals exactly 10% of item subtotal and the resulting subtotal/total uses the calculated discounted amount.

  # B-TC-026 | edge | P1 | AC1 | AC1
  Scenario: Percentage discount uses discounted subtotal for downstream calculations
    Given Feature is available with required test data.
    When Apply SAVE10 and inspect subtotal, shipping and tax calculations.
    Then Discount applies to item subtotal only; shipping and tax are calculated from the discounted subtotal.

  # B-TC-027 | boundary | P0 | AC2 | AC2
  Scenario: Fixed-code minimum threshold
    Given Feature is available with required test data.
    When Apply FLAT200 at ₹999, ₹1000 and ₹1001.
    Then ₹999 is rejected; ₹1000 and ₹1001 are eligible and receive ₹200 off.

  # B-TC-028 | edge | P1 | AC2 | AC2
  Scenario: Fixed discount affects only subtotal
    Given Feature is available with required test data.
    When Apply FLAT200 at ₹1500 and inspect order breakdown.
    Then Exactly ₹200 is removed from item subtotal and shipping/tax use the discounted subtotal.

  # B-TC-029 | boundary | P0 | AC3 | AC3
  Scenario: Minimum subtotal boundary
    Given Feature is available with required test data.
    When Apply FLAT200 at ₹999, ₹1000 and ₹1001.
    Then Only ₹1000 and above meet the minimum requirement.

  # B-TC-030 | edge | P1 | AC3 | AC3
  Scenario: Minimum threshold after cart change
    Given Feature is available with required test data.
    When Apply FLAT200 to an eligible cart, then remove items until subtotal is below ₹1000.
    Then The discount is revalidated and removed once the cart becomes ineligible.

  # B-TC-031 | boundary | P0 | AC4 | AC4
  Scenario: Expiry timing boundary
    Given Feature is available with required test data.
    When Apply immediately before expiry, at expiry, and after expiry.
    Then The code is accepted only while within its validity window and rejected once expired.

  # B-TC-032 | edge | P1 | AC4 | AC4
  Scenario: Expired code does not overwrite existing valid discount
    Given Feature is available with required test data.
    When Attempt to replace a valid code with an expired code.
    Then The expired code is rejected and the existing valid discount remains unchanged.

  # B-TC-033 | boundary | P0 | AC5 | AC5
  Scenario: Invalid code around valid identifier
    Given Feature is available with required test data.
    When Compare SAVE10 with a one-character mutation and an unknown code.
    Then Only the exact valid code is accepted; invalid variants are rejected without changing the total.

  # B-TC-034 | edge | P1 | AC5 | AC5
  Scenario: Invalid code cannot replace valid code
    Given Feature is available with required test data.
    When Attempt to apply a non-existent second code when a valid promo is already applied.
    Then The invalid code is rejected and the existing discount remains intact.

  # B-TC-035 | boundary | P0 | AC6 | AC6
  Scenario: Mixed-case promo variants
    Given Feature is available with required test data.
    When Apply save10, SAVE10 and SaVe10 separately.
    Then Each variant produces the same discount and order total.

  # B-TC-036 | edge | P1 | AC6 | AC6
  Scenario: Case normalization with whitespace
    Given Feature is available with required test data.
    When Apply '  save10  '.
    Then Whitespace is trimmed and case is normalized so the valid code is applied once.

  # B-TC-037 | boundary | P0 | AC7 | AC7
  Scenario: First redemption versus second redemption
    Given Feature is available with required test data.
    When Redeem once, then immediately attempt a second redemption as the same customer.
    Then First redemption succeeds; second redemption is rejected.

  # B-TC-038 | edge | P1 | AC7 | AC7
  Scenario: Single-use limit is per customer
    Given Feature is available with required test data.
    When Customer A redeemed the code; Customer B has not. Apply the code as Customer B.
    Then Customer B can use the code if otherwise valid; Customer A cannot reuse it.

  # B-TC-039 | boundary | P0 | AC8 | AC8
  Scenario: Fixed discount cap boundaries
    Given Feature is available with required test data.
    When Apply FLAT200 to subtotals ₹150, ₹200 and ₹201.
    Then Results are ₹0, ₹0 and ₹1 respectively; the discounted subtotal never goes below ₹0.

  # B-TC-040 | edge | P1 | AC8 | AC8
  Scenario: Capped discount preserves downstream calculations
    Given Feature is available with required test data.
    When Apply FLAT200 at subtotal ₹150 and inspect order breakdown.
    Then Discounted subtotal is ₹0 and downstream calculations use the defined discounted subtotal without negative values.

  # B-TC-041 | boundary | P0 | AC9 | AC9
  Scenario: Confirm replacement removes old discount
    Given Feature is available with required test data.
    When Apply second code and confirm replacement.
    Then Only the new discount is present; the old discount is fully removed and total is recalculated once.

  # B-TC-042 | edge | P1 | AC9 | AC9
  Scenario: Second code cannot stack with first
    Given Feature is available with required test data.
    When Apply a second code and inspect order summary before and after confirmation.
    Then No stacked discounts exist; confirmation is required and only one code remains applied.

  # B-TC-043 | boundary | P0 | AC10 | AC10
  Scenario: Whitespace-only promo input
    Given Feature is available with required test data.
    When Enter spaces/tabs only and click Apply.
    Then The input is treated as empty and the required-code message is shown.

  # B-TC-044 | edge | P1 | AC10 | AC10
  Scenario: Empty apply does not replace existing promo
    Given Feature is available with required test data.
    When Clear the input and click Apply while a valid promo is already applied.
    Then The existing applied code and discount remain unchanged; empty input does not clear the active promotion.

  # B-TC-045 | boundary | P0 | AC11 | AC11
  Scenario: Whitespace variants
    Given Feature is available with required test data.
    When Test leading-only, trailing-only, and leading+trailing spaces.
    Then All permitted leading/trailing whitespace is trimmed before validation.

  # B-TC-046 | edge | P1 | AC11 | AC11
  Scenario: Internal whitespace is not silently removed
    Given Feature is available with required test data.
    When Apply 'SA VE10' and compare with ' SAVE10 '.
    Then Only leading/trailing spaces are trimmed; internal whitespace does not become a valid code unless explicitly supported.

  # B-TC-047 | boundary | P0 | AC12 | AC12
  Scenario: Cart-change minimum threshold
    Given Feature is available with required test data.
    When Change subtotal to ₹1001, ₹1000 and ₹999 after applying FLAT200.
    Then The promo remains valid at ₹1000/above and is removed below ₹1000.

  # B-TC-048 | edge | P1 | AC12 | AC12
  Scenario: Cart increase and decrease recalculate discount
    Given Feature is available with required test data.
    When Increase subtotal, decrease it while eligible, then decrease it below eligibility.
    Then Discount and total are recalculated after each cart change and eligibility is enforced.
