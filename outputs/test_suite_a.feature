Feature: User Login
  Test cases generated from acceptance criteria

  Scenario: AC1: User can log in with valid username and password
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✓ User can log in with valid username and password

  Scenario: AC1: User can log in with valid username and password (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Request rejected

  Scenario: AC2: User cannot log in with invalid password (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Error: Invalid username or password

  Scenario: AC3: User cannot log in with non-existent username (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Error: Invalid username or password

  Scenario: AC4: User cannot log in with empty username (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Error: Username is required

  Scenario: AC5: User cannot log in with empty password (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Error: Password is required

  Scenario: AC6: Account locks after 5 failed login attempts (negative)
    Given Open login page
    And Enter username
    And Enter invalid password
    And Click login button
    And Verify error message is displayed
    Then ✗ Error: Account locked. Please contact support.

  Scenario: AC7: User session expires after 30 minutes of inactivity (negative)
    Given Execute step 1
    And Execute step 2
    And Verify result
    Then ✗ Error: Session expired. Please log in again.

  Scenario: AC8: User must accept terms and conditions before first login (negative)
    Given Open login page
    And Enter username
    And Enter invalid password
    And Click login button
    And Verify error message is displayed
    Then ✗ Error: You must accept the terms and conditions

