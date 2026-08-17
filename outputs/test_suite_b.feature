Feature: Apply Promo Code at Checkout
  Test cases generated from acceptance criteria

  Scenario: AC1: User can apply a valid promo code and receive discount
    Given Navigate to checkout
    And Enter valid promo code
    And Apply promo code
    And Verify discount is applied
    And Verify total is recalculated
    Then ✓ User can apply a valid promo code and receive discount

  Scenario: AC1: User can apply a valid promo code and receive discount (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Request rejected

  Scenario: AC2: User cannot apply an invalid promo code (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Error: Invalid promo code

  Scenario: AC3: User cannot apply an expired promo code (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Error: Promo code has expired

  Scenario: AC4: Promo code is case-insensitive
    Given Navigate to checkout
    And Enter valid promo code
    And Apply promo code
    And Verify discount is applied
    And Verify total is recalculated
    Then ✓ Promo code is case-insensitive

  Scenario: AC4: Promo code is case-insensitive (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Request rejected

  Scenario: AC5: User cannot apply promo code that has reached usage limit (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Error: Promo code usage limit reached

  Scenario: AC6: User cannot apply empty promo code (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Error: Promo code is required

  Scenario: AC7: Single-use promo code cannot be reused (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Error: Promo code already used

  Scenario: AC8: Multi-use promo code can be applied multiple times within limit
    Given Navigate to checkout
    And Enter valid promo code
    And Apply promo code
    And Verify discount is applied
    And Verify total is recalculated
    Then ✓ Multi-use promo code can be applied multiple times within limit

  Scenario: AC8: Multi-use promo code can be applied multiple times within limit (negative)
    Given Navigate to checkout
    And Enter promo code
    And Apply promo code
    And Verify error message
    Then ✗ Request rejected

  Scenario: AC9: Discount is calculated before tax
    Given Navigate to checkout
    And Enter valid promo code
    And Apply promo code
    And Verify discount is applied
    And Verify total is recalculated
    Then ✓ Discount is calculated before tax

