---
description: Perform a detailed review of the implemented code against the plan, spec, and constitution.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Review the implemented source code for correctness, quality, and adherence to the project artifacts and constitution.

Execution steps:

1.  **Load Contextual Artifacts**:
    -   Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.
    -   **REQUIRED**: Read `spec.md`, `plan.md`, and `tasks.md` for requirements and task coverage.
    -   **REQUIRED**: Read constitution file (path from AVAILABLE_DOCS or `.specify/memory/constitution.md`) for principles.
    -   Parse constitution.md to extract actual principle names and requirements (do not assume specific principles).
    -   **IF EXISTS**: Read `research.md` for technical decisions and constraints.
    -   **IF EXISTS**: Read `data-model.md` for entity definitions.
    -   **IF EXISTS**: Read all contract files in `contracts/` directory for API specifications.

2.  **Extract Target Files from tasks.md**:
    -   Parse tasks.md to extract all file paths mentioned in task descriptions.
    -   File paths can appear in multiple formats:
      * In parentheses: "T045: Implement auth (lib/auth.py, tests/test_auth.py)"
      * After colon: "T046: Create database - file: lib/db.py"
      * In description text
    -   Use pattern matching to extract file paths with common extensions (.py, .js, .ts, .go, .rb, etc.).
    -   Build a list of files that SHOULD have been created or modified.
    -   Extract both implementation files and test files (paths as defined in tasks.md).
    -   This is the **review scope** - only these files will be reviewed.
    -   File paths follow the project structure defined in plan.md.

3.  **Verify Implementation Completeness**:
    -   For each file in the review scope:
      * Check if the file exists (if marked [X] in tasks.md, it MUST exist).
      * Read the file content if it exists.
      * Verify file is not empty or just a stub (check for substantial content).
      * If file is missing but task is marked [X]: Add CRITICAL finding "Task T### marked complete but file missing".
      * If file exists but is empty/stub and task is marked [X]: Add HIGH finding "Task T### marked complete but file is empty/incomplete".
    -   Check for unexpected modifications (scope creep detection):
      * If git repo:
        1. Determine the default branch name:
           - Run `git symbolic-ref --short refs/remotes/origin/HEAD` and strip the `origin/` prefix if it succeeds.
           - If that fails, list remote branches with `git branch -r` and select `origin/main` or `origin/master` if available.
           - If no default branch can be resolved, log a warning and skip scope creep detection instead of failing.
        2. Once a branch name is available, run `git diff --name-only $(git merge-base HEAD <default_branch>)...HEAD`.
        3. If `git merge-base` fails (e.g., branch is new or diverged), report the condition and skip the scope creep check.
      * If not git repo: Compare file modification times or skip scope creep check (log warning).
      * Flag files modified but NOT mentioned in tasks.md as MEDIUM finding "Scope creep: file modified but not in tasks.md".
    -   If NO files exist from the review scope: Report "No implemented code found for this feature" and abort.

4.  **Perform Review Against Constitution**:
    -   For each principle extracted from constitution.md in step 1, evaluate ONLY the files in review scope.
    -   For each principle:
      * Identify relevant code patterns or requirements from the principle.
      * Check if the implementation adheres to the principle.
      * Assign rating: Excellent, Good, Needs Improvement, Violates.
      * Document specific examples from code that support the rating.
      * Flag violations as CRITICAL findings.

5.  **Perform Review Against Plan and Tasks**:
    -   **Task Coverage**: Does the implemented code cover all the tasks marked [X] in `tasks.md`? Note any tasks marked complete but with missing/incomplete implementation.
    -   **Architectural Adherence**: Does the code follow the architecture, libraries, and patterns defined in `plan.md` and `research.md`?
    -   **File Organization**: Are files placed in the correct directories as specified in plan.md?

6.  **Detailed Code Analysis** (only for files in review scope):
    -   Identify potential bugs, logical errors, or unhandled edge cases.
    -   Look for anti-patterns, overly complex code, or areas that could be simplified.
    -   Check for hardcoded secrets or configuration that should be externalized.
    -   Verify error handling and edge cases from spec.md are implemented.
    -   Suggest improvements for clarity, efficiency, and maintainability.

7.  **Create FEATURE_DIR/review-findings.md**:
    -   Generate a comprehensive, trackable findings file (this is the ONLY file output - do not create a separate report).
    -   Structure the file as follows:

    **Header Section:**
    -   Feature name and review date.
    -   Review scope: List all files that were reviewed (from tasks.md).
    -   High-level summary of implementation quality and completeness.

    **Summary Metrics:**
    -   Total findings: N (with breakdown: X CRITICAL, Y HIGH, Z MEDIUM, W LOW).
    -   Severity completion checkboxes: [ ] All CRITICAL fixed, [ ] All HIGH fixed, etc.
    -   Constitutional principle ratings table.

    **Findings Section** (grouped by severity):
    -   Use trackable format similar to tasks.md.
    -   Status checkboxes: [ ] Open, [X] Fixed (claimed), [✓] Verified, [!] Regression, [~] Won't fix.
    -   Each finding includes:
      * ID (R001, R002, etc. - stable and deterministic).
      * Status checkbox.
      * Severity (CRITICAL/HIGH/MEDIUM/LOW).
      * File(s):line number.
      * Description.
      * Recommendation.
      * Related Task (T### reference).
      * Fixed in: (commit hash field - empty initially).

    **Severity Assignment:**
    -   CRITICAL: Violates constitution, major bug, security issue.
    -   HIGH: Missed requirement, broken functionality.
    -   MEDIUM: Bad practice, refactoring needed, incomplete error handling.
    -   LOW: Style issues, minor improvements, optimization suggestions.

    **Include scope findings:**
    -   Files missing from tasks but tasks marked [X].
    -   Files modified unexpectedly (scope creep).
    -   Tasks marked complete but implementation empty/incomplete.

8.  **Suggest Next Steps**:
    -   Provide finding summary: "Found N issues in M files: X CRITICAL, Y HIGH, Z MEDIUM, W LOW".
    -   If CRITICAL or HIGH findings exist: "Review findings in review-findings.md. Recommend running /fix to address issues.".
    -   If only MEDIUM/LOW: "Implementation looks solid. Minor improvements suggested in review-findings.md. Ready to proceed or run /fix for polish.".
    -   If zero findings: "Implementation looks excellent! Ready for /ship.".

9.  **Offer Interactive Remediation**:
    -   Ask: "Would you like me to apply fixes for [CRITICAL/HIGH/all] severity issues? (yes/no/selective)".
    -   If yes: Explain that /fix command should be run to systematically address findings.
    -   If selective: Prompt for specific finding IDs to address.

Behavior rules:
-   Be constructive. The goal is to improve the code, not just criticize it.
-   Base the review only on the files you have read.
-   Prioritize findings based on their impact.
-   NEVER modify code during review - only generate reports and findings files.
-   Finding IDs must be stable and deterministic (R001, R002, etc.).
