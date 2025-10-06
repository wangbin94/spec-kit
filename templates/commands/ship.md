---
description: Run release-readiness checks and prepare for shipping the feature branch.
scripts:
  sh: scripts/ship.py
  ps: scripts/ship.py
---

The user input can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Confirm the feature branch is ready to ship by checking for outstanding findings, running the portfolio refresher, and surfacing any git workspace blockers. Provide a clear set of next steps (manual git commands, release notes, etc.)—do not auto-commit or merge unless the user explicitly requests staging.

Execution steps:

1. Run `{SCRIPT}` from the repository root. The script outputs release status and updates `.specify/state/features.yaml`.
   - Use `--json` if you need structured data for additional processing.

2. Interpret the results:
   - If `ready` is `false` or blockers are listed, enumerate them for the user (e.g., non-verified features, dirty git tree, regressions).
   - If `ready` is `true`, confirm that all features are verified and the workspace is clean.

3. If the git workspace is not clean, present the staged/unstaged/untracked file lists. Highlight `feature_files` (pending files inside `specs/<feature-branch>/` or listed in `tasks.md`) and ask whether the user wants to stage the entire set in one step:
   - Show the exact `git add` commands you plan to run before executing anything.
   - After staging, re-run `{SCRIPT} --json` to show the updated status.

4. Provide tailored next steps:
   - Unresolved findings → recommend rerunning `/verify` or `/fix`.
   - Dirty git state → suggest `git status`, `git add`, `git commit` as appropriate.
   - Ready to ship → prompt the user to tag, push, or open a release PR (you may show example git commands but never execute them).

5. Remind the user to run any project-specific regression or deployment scripts if required (mention known conventions if available).

Behavior rules:
- Do **not** run git commit, push, or merge operations automatically—only report and recommend. Staging via `git add` must be preceded by explicit user consent.
- Treat the reporter’s findings as authoritative; do not override or re-classify statuses manually.
- Ensure `.specify/state/features.yaml` is present after completion but do not include it in git operations.
- If no features exist yet, explain that shipping isn’t applicable and suggest starting with `/discover` or `/specify`.
