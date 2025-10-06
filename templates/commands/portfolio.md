---
description: Summarise feature portfolio status across all specs and update the registry
scripts:
  sh: scripts/bash/portfolio.sh
  ps: scripts/powershell/portfolio.ps1
---

The user input can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Goal: Provide a portfolio-level snapshot of every feature directory in `specs/`, including lifecycle status, review progress, and outstanding risks.

Execution steps:

1. Run `{SCRIPT}` from the repository root. This updates `.specify/state/features.yaml` and prints a summary table (or JSON if the user requests it).
   -   Default output: table sorted by lifecycle status → feature id
   -   `--json`: machine readable summary
   -   `--no-write`: diagnostic mode (skip registry refresh)

2. Review the generated data:
   -   Status progression: `spec → planning → implementing → reviewing → fixing → verified`
   -   Flags for regressions (`regression` status) or outstanding open findings
   -   Latest activity timestamp per feature

3. Highlight portfolio risks:
   -   Call out features stuck in `reviewing`/`fixing` with high open counts
   -   Note any regressions or missing artifacts (spec/plan/tasks/review-findings)
   -   Identify oldest features without progress

4. Suggest next actions for the team:
   -   Which features should move to review/fix/verify next
   -   Recommend running `/fix` or `/verify` where appropriate
   -   Surface features lacking core artifacts that need attention

Behavior rules:
-   Never modify feature artifacts directly—only read and report
-   Prefer surfacing actionable insights over raw counts
-   Keep the portfolio view deterministic for auditable history
-   If no features exist, explain how to create one (`.specify/scripts/bash/create-new-feature.sh`)
