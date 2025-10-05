---
description: Verify that fixes resolved review findings without introducing regressions
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Verify that fixes marked [X] in review-findings.md actually resolved the issues and didn't introduce regressions.

Execution steps:

1.  **Load Review Findings**:
    -   Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.
    -   Read FEATURE_DIR/review-findings.md.
    -   If review-findings.md doesn't exist: Report "No review findings found. Run /review first." and abort.
    -   Parse all findings with status [X] (claimed fixed).
    -   If no [X] findings: Report "No fixes to verify. Run /fix first." and abort.
    -   Group findings by file for efficient verification.

2.  **Display Verification Scope**:
    -   Show what will be verified:
      ```
      Verifying 7 claimed fixes:
        [X] R001: Database persistence (lib/db.py:45)
        [X] R002: Error handling (lib/client.py:67)
        [X] R003: Authentication check (lib/api.py:23)
        ...

      Files in scope:
        - lib/db.py
        - lib/client.py
        - lib/api.py
      ```

3.  **Load Context**:
    -   Read spec.md and plan.md for requirements.
    -   Read constitution.md for principles.
    -   For each file in verification scope:
      * Read current file content.
      * Read associated test files if they exist.

4.  **Verify Each Fix**:
    -   For each finding marked [X]:
      * Re-read the specific file:line mentioned.
      * Check if the original issue still exists.
      * Verify the recommendation was properly implemented.
      * Check if the fix follows the spec/plan/constitution.
      * Verify code quality of the fix (no anti-patterns).

    -   Categorize verification result:
      * VERIFIED: Issue is resolved, implementation is correct.
      * STILL_BROKEN: Issue still exists or partially fixed.
      * REGRESSION: Fix introduced new issues.
      * INCOMPLETE: Fix is there but doesn't fully address the issue.

5.  **Run Tests for Verification**:
    -   Run full test suite (not just affected tests):
      * Python: pytest tests/ -v --cov
      * Node: npm test -- --coverage
      * Go: go test ./...
    -   Compare test results with previous runs:
      * Any new test failures? → REGRESSION
      * Did tests related to fixes pass? → Supports VERIFIED
      * Coverage increased? → Good sign
    -   If test results are available from /test command, compare against baseline.

6.  **Detect Regressions**:
    -   For each modified file:
      * Check if changes affected other functionality.
      * Look for new errors, warnings, or linting issues.
      * Verify imports/dependencies still work.
      * Check if related code still makes sense.
    -   Run git diff on modified files to see extent of changes:
      * Determine the default branch before calling merge-base:
        1. Try `git symbolic-ref --short refs/remotes/origin/HEAD` and remove the `origin/` prefix if present.
        2. If that fails, inspect `git branch -r` for `origin/main` or `origin/master`.
        3. If no branch can be resolved, emit a warning and skip the diff step.
      * When a branch exists, run `git diff --stat $(git merge-base HEAD <default_branch>)...HEAD` (or similar scope) and handle merge-base failures by reporting them without aborting.
      * Large unexpected changes? → Flag for manual review.
      * Changes outside the fix scope? → Potential regression.

7.  **Update review-findings.md**:
    -   For each verified finding:
      * [X] → [✓] (verified fixed).
      * Add verification timestamp.
      * Add note: "Verified: <date>".

    -   For findings still broken:
      * [X] → [ ] (revert to open).
      * Add note: "Verification failed: <reason>".

    -   For regressions:
      * [X] → [!] (regression detected).
      * Add note: "REGRESSION: <description of new issue>".
      * Create new finding for the regression.

    -   For incomplete fixes:
      * [X] → [ ] (revert to open).
      * Update description to note what's still missing.

    -   Update summary metrics:
      * Update completion checkboxes.
      * Track: Verified, Still broken, Regressions.

8.  **Generate Verification Report**:
    -   Create detailed report:
      ```
      Verification Results:

      ✓ VERIFIED (5):
        [✓] R001: Database persistence - confirmed working
        [✓] R002: Error handling - properly implemented
        [✓] R003: Authentication check - verified
        [✓] R004: Input validation - tests passing
        [✓] R005: Logging added - confirmed

      ✗ STILL BROKEN (1):
        [ ] R006: Performance issue - fix incomplete, still times out

      ! REGRESSIONS (1):
        [!] R007: Cache invalidation - fix broke related feature
            New issue: Cache not clearing on update (lib/cache.py:89)
            Created new finding: R011

      Test Results:
        Total: 45 passed, 1 failed
        Coverage: 87% (+5% from previous)
        New failures: test_cache_invalidation (caused by R007 fix)

      Modified files verified:
        ✓ lib/db.py - clean
        ✓ lib/client.py - clean
        ✓ lib/api.py - clean
        ! lib/cache.py - regression detected
      ```

9.  **Suggest Next Steps**:
    -   If all verified (all [✓]):
      * "All fixes verified! Ready to run /ship.".

    -   If some still broken or regressions:
      * "Verification found issues:".
      * "  - N findings still broken: R###, R###".
      * "  - M regressions detected: R###, R###".
      * "Recommend: Fix remaining issues before proceeding.".
      * "Run /fix again to address: R###, R###, R###".

    -   If regressions detected:
      * "⚠️  CRITICAL: Fixes introduced regressions. Address immediately.".
      * "Review new findings: R###, R###".

    -   If mostly clean with minor issues:
      * "Verification mostly successful. N/M fixes verified.".
      * "Minor issues remain - may proceed or fix for polish.".

Behavior rules:
-   Re-run verification from scratch - don't trust previous claims.
-   Always run tests to catch regressions.
-   Be strict - partial fixes should be marked incomplete.
-   Create new findings for regressions detected.
-   Never modify code during verification - only update review-findings.md.
-   Document why verification failed for each finding.
-   If unsure whether fix is complete, mark as incomplete (conservative approach).
-   Compare against spec/plan requirements, not just "does it work".
