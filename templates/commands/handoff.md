---
description: Capture an end-of-session handoff summary so future `/resume` runs can pick up context instantly (works for any repository, not only Spec Kit).
scripts:
  sh: scripts/bash/check-prerequisites.sh --paths-only --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Store a durable snapshot of the current work state, outstanding tasks, and next-step intent so the next session can resume without re-triaging. Supports general projects; no parameters required (auto-detects context), but optional overrides are honored. When Spec Kit artifacts exist, include them; otherwise rely on repository activity (files, folders, commands supplied by the user).

Execution steps:

1. Determine repository context:
   - Try running `{SCRIPT}` from the repository root to retrieve JSON with `REPO_ROOT` and `BRANCH`. If it fails (common for non-Specify projects), fall back to:
     * `REPO_ROOT` = `git rev-parse --show-toplevel` (if Git) or the present working directory.
     * `BRANCH` = current Git branch (`git rev-parse --abbrev-ref HEAD`) or `"N/A"` if Git isn’t available.
   - Capture environment overrides: `SPECIFY_FEATURE`, `SPECIFY_CONTEXT`, or similar variables should be recorded if set.

2. Resolve the handoff context identifier (`context_label`) using the first value that exists:
   1. Argument override such as `context=<name>` or `feature=<slug>` from `$ARGUMENTS`.
   2. `SPECIFY_FEATURE` or `SPECIFY_CONTEXT` environment variables.
   3. Current Git branch name (if not `HEAD`/`N/A`).
   4. Default to `"session"`.
   Normalize the label by lowercasing and replacing spaces with hyphens.

3. Collect project signals to include in the handoff (these should work even when no arguments are supplied):
   - `git status --short` output (if Git exists) to list staged/unstaged files; limit to the 10 most recent and derive a distinct list of touched directories.
   - A quick change summary (`git diff --stat` limited to the latest 10 entries) to quantify work done in this session.
   - The most recent commit summary (`git log -1 --oneline`) when available.
   - If Spec Kit artifacts exist (`specs/<context_label>/spec.md`, `plan.md`, `tasks.md`, etc.), gather highlight details such as outstanding `[NEEDS CLARIFICATION]` markers or next unchecked tasks.
   - When Spec Kit artifacts are absent, look for helpful context files (e.g., `TODO.md`, `CHANGELOG.md`, `docs/`) and surface notable open items if present.
   - Incorporate any user-provided notes from `$ARGUMENTS` (trim whitespace). If no notes are supplied, synthesize a concise summary from the detected signals (e.g., "Modified 3 files across src/api and tests/; pending tests to write").

4. Ensure the storage directory exists. Use `$REPO_ROOT/.specify/session/handoffs` when `.specify` is present; otherwise use `$REPO_ROOT/.session/handoffs`. Create directories as needed without deleting existing contents.

5. Compose a Markdown entry and append it to `{storage_dir}/{context_label}.md` (create the file if new):
   ```
   ## Handoff Summary - {timestamp_utc}
   - Context: {context_label}
   - Branch: {branch_label}
   - Working Directory: {REPO_ROOT}
   - Recent Commit: {git log snippet or "N/A"}
   - Modified Files:
     {bullet list from git status or "None"}
   - Affected Directories:
     {bullet list of directories derived from modified files or "None"}
   - Spec Kit Artifacts:
     {summaries if available, otherwise "Not detected"}
   - Notes:
     {user notes or synthesized summary}
   - Next Actions:
     {top outstanding tasks or recommendations gathered in step 3, otherwise a synthesized suggestion based on detected changes (e.g., "Finish writing tests for src/api/user.test.ts").}
   ```
   - Include outstanding clarifications or blockers under Notes/Next Actions when relevant.

6. Confirm success to the user:
   - Mention the saved file path.
   - Suggest starting the next session with `/resume context={context_label}` (or simply `/resume` when relying on auto-detection).
   - Echo the key points recorded so the user can verify accuracy.
