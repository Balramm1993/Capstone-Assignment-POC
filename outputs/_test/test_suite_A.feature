Feature: User Login

  # A-TC-001 | positive | P0 | AC1 | AC1
  Scenario: AC1: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC1: Given a registered, active user, when they enter their correct email and password and click Log In, then they are redirected to the dashboard.
    Then The system satisfies AC1 exactly, including the stated outcome and message/state.

  # A-TC-002 | negative | P1 | AC1 | AC1
  Scenario: Reject a prohibited or invalid condition
    Given Feature is available.
    When Exercise AC1 with an invalid, missing, unauthorized, expired, or prohibited condition relevant to the criterion.
    Then The system rejects the invalid condition and preserves the required state/error behavior.

  # A-TC-003 | positive | P0 | AC2 | AC2
  Scenario: AC2: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC2: Given a registered user, when they enter a correct email but wrong password, then an error "Invalid email or password" is shown and they remain on the login page.
    Then The system satisfies AC2 exactly, including the stated outcome and message/state.

  # A-TC-004 | negative | P0 | AC2 | AC2
  Scenario: Wrong password stays on login
    Given Feature is available with required test data.
    When Enter correct email and wrong password; click Log In.
    Then Exactly 'Invalid email or password' is shown and the user remains on the login page.

  # A-TC-005 | positive | P0 | AC3 | AC3
  Scenario: AC3: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC3: When an email that is not registered is entered with any password, then the same generic "Invalid email or password" error is shown (no indication of whether the email exists).
    Then The system satisfies AC3 exactly, including the stated outcome and message/state.

  # A-TC-006 | negative | P0 | AC3 | AC3
  Scenario: Unknown email cannot be enumerated
    Given Feature is available with required test data.
    When Enter an unregistered email with a password and submit.
    Then The exact generic 'Invalid email or password' message is shown; no indication reveals whether the email exists.

  # A-TC-007 | positive | P0 | AC4 | AC4
  Scenario: AC4: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC4: When either field is left blank and Log In is clicked, then inline validation prompts the user to fill the required field(s); no request is sent.
    Then The system satisfies AC4 exactly, including the stated outcome and message/state.

  # A-TC-008 | negative | P0 | AC4 | AC4
  Scenario: Blank required fields are validated inline
    Given Feature is available with required test data.
    When Leave email blank, password blank, then each field blank separately; click Log In.
    Then Inline required-field prompts identify the missing field(s), and no authentication request is sent.

  # A-TC-009 | positive | P0 | AC5 | AC5
  Scenario: AC5: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC5: When the email field contains a value that is not a valid email format, then an inline "Enter a valid email address" message is shown.
    Then The system satisfies AC5 exactly, including the stated outcome and message/state.

  # A-TC-010 | negative | P0 | AC5 | AC5
  Scenario: Malformed email formats
    Given Feature is available with required test data.
    When Submit user, user@, @example.com, user@@example.com and user name@example.com.
    Then Each malformed email shows inline 'Enter a valid email address'.

  # A-TC-011 | positive | P0 | AC6 | AC6
  Scenario: AC6: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC6: After 5 consecutive failed attempts within 15 minutes, the account is temporarily locked for 30 minutes and a "Your account is locked. Try again later." message is shown, even if correct credentials are subsequently entered.
    Then The system satisfies AC6 exactly, including the stated outcome and message/state.

  # A-TC-012 | negative | P0 | AC6 | AC6
  Scenario: Five failures lock the account
    Given Feature is available with required test data.
    When Submit 5 consecutive wrong-password attempts within 15 minutes, then submit correct credentials.
    Then After the fifth failure the account is locked for 30 minutes and correct credentials still show 'Your account is locked. Try again later.'.

  # A-TC-013 | positive | P0 | AC7 | AC7
  Scenario: AC7: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC7: The email is case-insensitive (User@x.com == user@x.com); the password is case-sensitive.
    Then The system satisfies AC7 exactly, including the stated outcome and message/state.

  # A-TC-014 | negative | P0 | AC7 | AC7
  Scenario: Password casing is significant
    Given Feature is available with required test data.
    When Use the correct email but alter password casing.
    Then Authentication fails because the password is case-sensitive.

  # A-TC-015 | positive | P0 | AC8 | AC8
  Scenario: AC8: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC8: On successful login a session is established; on browser refresh the user remains logged in until the session expires (24 hours) or they log out.
    Then The system satisfies AC8 exactly, including the stated outcome and message/state.

  # A-TC-016 | negative | P0 | AC8 | AC8
  Scenario: Expired session cannot access dashboard
    Given Feature is available with required test data.
    When Refresh or navigate to the dashboard after expiry.
    Then The user is no longer authenticated and must log in again.

  # A-TC-017 | positive | P0 | AC9 | AC9
  Scenario: AC9: verify the required behavior
    Given Required feature state and valid test data are available.
    When Execute the exact condition described in AC9: A user whose account is deactivated sees "This account is inactive. Contact support." and is not logged in.
    Then The system satisfies AC9 exactly, including the stated outcome and message/state.

  # A-TC-018 | negative | P0 | AC9 | AC9
  Scenario: Inactive account is not authenticated
    Given Feature is available with required test data.
    When Enter the inactive user's correct email and password.
    Then The exact 'This account is inactive. Contact support.' message is shown and no authenticated session is created.

  # A-TC-019 | boundary | P0 | AC1 | AC1
  Scenario: Password length rule
    Given Feature is available with required test data.
    When Use a valid account and try password lengths 7, 8, 64, and 65.
    Then 8 and 64 character passwords are accepted; 7 and 65 character passwords are rejected according to the password constraint.

  # A-TC-020 | edge | P1 | AC1 | AC1
  Scenario: Session starts after successful login
    Given Feature is available with required test data.
    When Log in successfully and inspect authenticated state/session.
    Then A session is established and the user is authenticated on the dashboard.

  # A-TC-021 | boundary | P1 | AC2 | AC2
  Scenario: Verify the nearest requirement boundary
    Given Boundary values are available.
    When Test values immediately below, at, and immediately above the threshold or limit stated/implied by AC2.
    Then Behavior changes only at the defined boundary and remains compliant with the requirement.

  # A-TC-022 | edge | P1 | AC2 | AC2
  Scenario: Failed login contributes to lockout
    Given Feature is available with required test data.
    When Submit consecutive wrong passwords and count failures.
    Then Each failed authentication is rejected and the failures contribute to the AC6 lockout threshold.

  # A-TC-023 | boundary | P0 | AC3 | AC3
  Scenario: Unknown email with password length boundaries
    Given Feature is available with required test data.
    When Submit the unknown email with passwords of 8 and 64 characters.
    Then The same generic authentication error is returned without account enumeration.

  # A-TC-024 | edge | P1 | AC3 | AC3
  Scenario: Registered-wrong-password and unknown-email responses match
    Given Feature is available with required test data.
    When Compare registered+wrong-password with unregistered+any-password.
    Then Both paths expose the same generic authentication error and do not reveal account existence.

  # A-TC-025 | boundary | P0 | AC4 | AC4
  Scenario: One blank field at a time
    Given Feature is available with required test data.
    When Test blank email with valid password, then valid email with blank password.
    Then Only the missing field is prompted and no authentication request is sent in either case.

  # A-TC-026 | edge | P1 | AC4 | AC4
  Scenario: Whitespace-only required fields
    Given Feature is available with required test data.
    When Enter whitespace-only values in email/password and click Log In.
    Then The UI treats whitespace-only required values as empty/invalid and does not send authentication.

  # A-TC-027 | boundary | P0 | AC5 | AC5
  Scenario: Email format near valid boundary
    Given Feature is available with required test data.
    When Compare user@example.com with user@example and user@example.com.
    Then Only the valid email format proceeds past email-format validation; invalid formats show the exact inline message.

  # A-TC-028 | edge | P1 | AC5 | AC5
  Scenario: Email normalization does not bypass format validation
    Given Feature is available with required test data.
    When Try leading/trailing spaces and mixed-case valid email addresses.
    Then Valid formatted email remains valid after permitted normalization; malformed input still receives format validation.

  # A-TC-029 | boundary | P0 | AC6 | AC6
  Scenario: Lockout thresholds and time window
    Given Feature is available with required test data.
    When Compare 4 failures vs 5 failures; place failures inside and outside the 15-minute window.
    Then Four failures do not lock the account; five qualifying consecutive failures within 15 minutes do; failures outside the window do not incorrectly satisfy the threshold.

  # A-TC-030 | edge | P1 | AC6 | AC6
  Scenario: Lock expires after 30 minutes
    Given Feature is available with required test data.
    When Attempt correct credentials immediately, just before 30 minutes, and at/after 30 minutes.
    Then Correct credentials are rejected during the lock period and accepted after the 30-minute lock expires, subject to other account rules.

  # A-TC-031 | boundary | P0 | AC7 | AC7
  Scenario: Email casing permutations
    Given Feature is available with required test data.
    When Try User@x.com, user@x.com, USER@X.COM and mixed-case variants with the same password.
    Then All email-case variants authenticate as the same account.

  # A-TC-032 | edge | P1 | AC7 | AC7
  Scenario: Password case permutations
    Given Feature is available with required test data.
    When Try Password, password, PASSWORD and mixed-case variants.
    Then Only the exact registered password casing succeeds.

  # A-TC-033 | boundary | P0 | AC8 | AC8
  Scenario: Session expiry boundary
    Given Feature is available with required test data.
    When Refresh at 23:59:59 and then at 24:00:00 after login.
    Then The session remains valid before 24 hours and expires at the defined 24-hour boundary.

  # A-TC-034 | edge | P1 | AC8 | AC8
  Scenario: Refresh, logout and direct navigation session behavior
    Given Feature is available with required test data.
    When Refresh the dashboard, log out, refresh again, then navigate directly to the dashboard URL.
    Then Refresh preserves the active session; after logout, the session is invalid and protected navigation requires authentication.

  # A-TC-035 | boundary | P0 | AC9 | AC9
  Scenario: Inactive status blocks even correct credentials
    Given Feature is available with required test data.
    When Deactivate the account, then attempt login with previously valid credentials.
    Then The account is rejected after deactivation; valid credentials do not bypass inactive status.

  # A-TC-036 | edge | P1 | AC9 | AC9
  Scenario: Inactive account cannot establish session
    Given Feature is available with required test data.
    When Attempt login and inspect session/dashboard access.
    Then No authenticated session exists and protected pages remain inaccessible.
