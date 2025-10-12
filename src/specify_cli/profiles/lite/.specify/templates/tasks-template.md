# Tasks (Lite): [FEATURE]

**Input**: `plan.md` from `/specs/[###-feature-name]/`  
**Prerequisites**: plan complete, clarifications resolved enough to execute

## Execution Flow (Lite)
```
1. Parse plan.md for phases, components, and validation strategy.
2. Translate each phase into concrete tasks that reference real files or modules.
3. Keep the list lean (aim for 8–15 tasks). Merge tiny steps; split when blocking parallelism.
4. Mark [P] only when tasks touch independent files and have no ordering constraints.
5. Prioritize tests early, then implementation, then clean-up.
```

## Format: `[ID] [P?] Description`
- IDs increment sequentially (T001, T002, …)
- `[P]` marks tasks that can run in parallel with the previous one
- Include file paths or modules so another teammate (or agent) can act immediately

## Core Sequence
1. **Setup** – Ensure tooling, configs, and dependencies are ready.
2. **Tests First** – Define or extend failing tests that prove the feature works.
3. **Implementation** – Build the feature to satisfy the failing tests.
4. **Validation & Polish** – Clean up, document, and verify edge cases.

## Example Skeleton
- [ ] T001 Setup development environment adjustments in `Makefile` and `pyproject.toml`
- [ ] T002 Configure feature flag and baseline scaffolding in `src/app/__init__.py`
- [ ] T003 [P] Draft failing integration test case in `tests/integration/test_feature.py`
- [ ] T004 [P] Draft failing contract test for `/api/feature` in `tests/contract/test_feature.py`
- [ ] T005 Implement core feature flow in `src/app/feature.py` to satisfy tests
- [ ] T006 Wire data persistence and validation in `src/app/store.py`
- [ ] T007 Update docs or usage notes in `docs/feature.md`
- [ ] T008 Run test suite and final verification checklist

## Dependency Notes
- Tests that touch different modules can be parallelized.
- Keep implementation tasks in dependency order (models → services → API).
- Ensure documentation or manual QA steps happen after implementation stabilizes.

## Validation Checklist
- [ ] Every major behavior in plan.md has at least one task
- [ ] Tests exist (or are planned) for each critical behavior
- [ ] Parallel tasks only when files truly do not conflict
- [ ] Final validation task ensures the feature is ready to ship

---

*Lite profile favors decisive, actionable tasks. Keep wording tight, avoid duplicating plan context, and aim for immediate executability.*
