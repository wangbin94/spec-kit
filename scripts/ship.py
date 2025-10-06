#!/usr/bin/env python3
"""Evaluate release readiness for the current repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set
import re


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

try:
    import portfolio  # type: ignore
except ImportError as exc:
    raise SystemExit(f"Unable to import portfolio utilities: {exc}")


@dataclass
class GitStatus:
    branch: str
    clean: bool
    staged_changes: bool
    untracked: bool
    staged_files: list[str]
    unstaged_files: list[str]
    untracked_files: list[str]


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".specify").is_dir() or (candidate / ".git").is_dir():
            return candidate
    return start


def run_git(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", *cmd], cwd=cwd, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(cmd)} failed")
    return result


def extract_task_paths(tasks_file: Path) -> Set[str]:
    if not tasks_file.exists():
        return set()
    pattern = re.compile(r"([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]+)")
    results: Set[str] = set()
    try:
        content = tasks_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return set()
    for line in content.splitlines():
        for match in pattern.findall(line):
            cleaned = match.strip().strip('`"\'')
            if cleaned:
                results.add(Path(cleaned).as_posix())
    return results


def collect_git_status(repo_root: Path) -> GitStatus:
    branch_proc = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    branch = branch_proc.stdout.strip()

    status_proc = run_git(["status", "--porcelain"], repo_root)
    staged = untracked = False
    clean = True
    staged_files: list[str] = []
    unstaged_files: list[str] = []
    untracked_files: list[str] = []
    for line in status_proc.stdout.splitlines():
        if not line.strip():
            continue
        clean = False
        if line.startswith("??"):
            untracked = True
            untracked_files.append(line[3:])
        else:
            staged = True
            index_status, work_status, path = line[0], line[1], line[3:]
            if index_status != " " and index_status != "?":
                staged_files.append(path)
            if work_status != " " and work_status != "?":
                unstaged_files.append(path)

    return GitStatus(
        branch=branch,
        clean=clean,
        staged_changes=staged,
        untracked=untracked,
        staged_files=staged_files,
        unstaged_files=unstaged_files,
        untracked_files=untracked_files,
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Release readiness reporter")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    args = parser.parse_args(argv or sys.argv[1:])

    repo_root = find_repo_root(Path.cwd())
    features = portfolio.gather_features(repo_root)
    portfolio.write_registry(repo_root, features)

    git_info = collect_git_status(repo_root)

    blockers: List[str] = []
    non_verified = [f for f in features if f.status != "verified"]
    if non_verified:
        blockers.append(f"{len(non_verified)} feature(s) still incomplete: " + ", ".join(f.feature_id for f in non_verified))

    if not git_info.clean:
        details = []
        if git_info.staged_files:
            details.append("staged files present")
        if git_info.unstaged_files:
            details.append("unstaged changes present")
        if git_info.untracked_files:
            details.append("untracked files present")
        blockers.append("Git workspace not clean: " + ", ".join(details))

    ready = not blockers

    summary_rows = []
    for record in features:
        summary_rows.append(
            {
                "feature": record.feature_id,
                "status": record.status,
                "open": record.findings.open,
                "claimed": record.findings.claimed,
                "verified": record.findings.verified,
                "regression": record.findings.regression,
                "updated": portfolio.isoformat(record.last_updated),
            }
        )

    feature_branch = git_info.branch if git_info.branch and git_info.branch[:3].isdigit() else None
    feature_prefix = f"specs/{feature_branch}/" if feature_branch else None
    task_paths: Set[str] = set()
    if feature_branch:
        for record in features:
            if record.feature_id == feature_branch:
                tasks_file = repo_root / record.feature_dir / "tasks.md"
                task_paths = extract_task_paths(tasks_file)
                break

    feature_related: list[str] = []
    if feature_prefix or task_paths:
        for group in (git_info.staged_files, git_info.unstaged_files, git_info.untracked_files):
            for path in group:
                include = False
                if feature_prefix and path.startswith(feature_prefix):
                    include = True
                elif task_paths and path in task_paths:
                    include = True
                if include and path not in feature_related:
                    feature_related.append(path)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": repo_root.as_posix(),
        "feature_branch": feature_branch,
        "git": {
            "branch": git_info.branch,
            "clean": git_info.clean,
            "staged_changes": git_info.staged_changes,
            "untracked": git_info.untracked,
            "staged_files": git_info.staged_files,
            "unstaged_files": git_info.unstaged_files,
            "untracked_files": git_info.untracked_files,
        },
        "feature_files": feature_related,
        "ready": ready,
        "blockers": blockers,
        "features": summary_rows,
        "tasks_paths": sorted(task_paths),
    }

    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"Repository: {repo_root}")
        print(f"Current branch: {git_info.branch}")
        print(f"Working tree clean: {'yes' if git_info.clean else 'no'}")
        print()
        if summary_rows:
            header = f"{'Feature':<20} {'Status':<13} {'Open':>4} {'Claimed':>7} {'Verified':>8} {'Reg':>4} {'Updated':<20}"
            print(header)
            print('-' * len(header))
            for row in summary_rows:
                updated = row['updated'] or '-'  # type: ignore[index]
                print(
                    f"{row['feature']:<20} {row['status']:<13} "
                    f"{row['open']:>4} {row['claimed']:>7} {row['verified']:>8} {row['regression']:>4} "
                    f"{updated:<20}"
                )
        else:
            print("No features specified yet.")
        print()
        def print_file_block(title: str, items: list[str]) -> None:
            if not items:
                return
            print(title)
            for path in items:
                print(f"  • {path}")
            print()

        print_file_block("Staged files:", git_info.staged_files)
        print_file_block("Unstaged files:", git_info.unstaged_files)
        print_file_block("Untracked files:", git_info.untracked_files)

        if feature_related:
            print("Feature-related pending files:")
            for path in feature_related:
                print(f"  • {path}")
            print()

        if ready:
            print("All checks passed. Ready to ship!")
        else:
            print("Blockers:")
            for item in blockers:
                print(f"- {item}")

        print()
        print("Suggested next steps:")
        if git_info.clean:
            print("- Tag commit or create release notes")
        else:
            if feature_related:
                print("- Stage feature files above (you can accept staging all of them in one step)")
            print("- Stage and commit any remaining files (see lists above)")
        if non_verified:
            print("- Re-run /verify after addressing open findings")
        print("- Consider: git status, git diff, git add <files>, git commit, git tag")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
