---
description: Apply fixes for review findings systematically
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Systematically fix issues identified in review-findings.md, mark them as fixed, and prepare for verification.

Execution steps:

1.  **Load Review Findings**:
    -   Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.
    -   Read FEATURE_DIR/review-findings.md
    -   If review-findings.md doesn't exist: Report "No review findings found. Run /review first." and abort.
    -   Parse all findings with status [ ] (Open)
    -   Group findings by severity: CRITICAL, HIGH, MEDIUM, LOW

2.  **Display Findings Summary**:
    -   Show findings grouped by severity with counts
    -   Format:
      ```
      CRITICAL (2):
        [ ] R001: Database not persisting data (lib/db.py:45)
        [ ] R003: Missing authentication check (lib/api.py:23)

      HIGH (5):
        [ ] R002: No error handling for API timeout (lib/client.py:67)
        ...

      MEDIUM (3): ...
      LOW (2): ...
      ```

3.  **Determine Fix Strategy**:
    -   If user provided arguments with specific finding IDs (e.g., "R001,R003,R005"):
      * Fix only those specific findings
    -   If user provided severity level (e.g., "CRITICAL", "HIGH"):
      * Fix all findings at that severity level
    -   If no arguments or "all":
      * Ask: "Which findings should I fix?"
        - [c] All CRITICAL only
        - [h] All CRITICAL + HIGH
        - [a] All findings
        - [s] Selective (specify IDs: R001,R003,R005)
        - [n] Cancel

4.  **Load Context for Fixing**:
    -   Read spec.md, plan.md, tasks.md for context
    -   Read constitution.md for principles
    -   Read research.md if it exists for technical constraints
    -   For each finding to fix:
      * Read the file(s) mentioned in the finding
      * Understand the current implementation
      * Review the recommendation from the finding

5.  **Apply Fixes Systematically**:
    -   Group fixes by file to minimize file operations
    -   For each file with fixes:
      * Apply all fixes for that file in one operation
      * Ensure fixes don't conflict with each other
      * Preserve code style and formatting
      * Add comments if the fix is non-obvious
    -   After applying fixes to a file:
      * Verify syntax is valid (run linter if available)
      * Check if file has associated tests
    -   Track which findings were successfully fixed

6.  **Run Affected Tests**:
    -   Identify test files related to fixed code
    -   Run tests for each modified file:
      * Python: pytest <test_file> -v
      * Node: npm test -- <test_file>
      * Go: go test <package>
    -   Track test results: pass/fail for each file
    -   If tests fail:
      * Mark finding as attempted but note test failure
      * Ask if should continue or stop

7.  **Update review-findings.md**:
    -   For each successfully fixed finding:
      * Change status from [ ] to [X]
      * Add note: "Fixed in: pending commit" (or commit hash if user commits during process)
      * Add timestamp of fix
    -   For findings that couldn't be fixed:
      * Add note explaining why (e.g., "Test failed", "Requires design decision", "Blocked by dependency")
    -   Update summary metrics:
      * Decrement open count
      * Show progress: "Fixed M/N findings"

8.  **Generate Fix Summary**:
    -   Report what was fixed:
      ```
      Fixed 7/10 findings:
        ✓ R001: Database persistence added
        ✓ R002: Error handling implemented
        ✓ R003: Authentication check added
        ...

      Could not fix (3):
        ✗ R008: Requires API design decision (blocked)
        ✗ R009: Test failed after fix (needs investigation)
        ✗ R010: Performance optimization (deferred to later)

      Modified files:
        - lib/db.py
        - lib/api.py
        - lib/client.py
        - tests/test_db.py
      ```

9.  **Suggest Next Steps**:
    -   If all fixes successful and tests pass:
      * "All fixes applied successfully! Run /verify to confirm fixes resolved the issues."
    -   If some fixes failed:
      * "Fixed X/Y findings. Review failures above. You may need to manually address: R###, R###"
    -   If fixes modified code:
      * "Modified N files. Consider committing changes before running /verify."
    -   Recommend: "Next: /verify to validate fixes"

10. **Refresh Portfolio Snapshot**:
    -   Run `scripts/bash/portfolio.sh` (or `scripts/powershell/portfolio.ps1` on Windows) from the repo root to update `.specify/state/features.yaml`.
    -   Verify the feature status progresses appropriately (e.g., from `reviewing` to `fixing`).

Behavior rules:
-   Apply fixes incrementally - one file at a time
-   Always preserve existing functionality
-   Add proper error handling and edge case coverage
-   Follow code style from existing codebase
-   Never skip tests - if tests fail, report it
-   Be conservative - if unsure about a fix, ask user
-   Document complex fixes with comments
-   Update review-findings.md after each successful fix
-   If a fix requires design decisions, flag it instead of guessing
