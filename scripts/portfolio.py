#!/usr/bin/env python3
"""Generate and report feature portfolio information for Spec Kit projects.

This script scans the `specs/` directory, derives feature status from artifact
availability (spec, plan, tasks, review findings), summarises review outcomes,
and writes a machine-readable registry under `.specify/state/features.yaml`.

It also prints either a human-readable table or JSON, depending on the invoked
flags. The script is intended to be called by thin Bash/PowerShell wrappers so
that the same logic is shared across platforms.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass
class FindingsSummary:
    open: int = 0
    claimed: int = 0
    verified: int = 0
    regression: int = 0
    wont_fix: int = 0


@dataclass
class FeatureRecord:
    feature_id: str
    title: str
    status: str
    spec_exists: bool
    plan_exists: bool
    tasks_exists: bool
    review_exists: bool
    findings: FindingsSummary
    last_updated: datetime | None
    feature_dir: Path

    @property
    def relative_path(self) -> str:
        return self.feature_dir.as_posix()


STATUS_ORDER = {
    "spec": 0,
    "planning": 1,
    "implementing": 2,
    "reviewing": 3,
    "fixing": 4,
    "regression": 5,
    "verified": 6,
}


def find_repo_root(start: Path) -> Path:
    """Walk up from *start* to locate repository root (has .specify or .git)."""

    for candidate in [start, *start.parents]:
        if (candidate / ".specify").is_dir() or (candidate / ".git").is_dir():
            return candidate
    return start


def read_spec_title(spec_path: Path) -> str:
    try:
        with spec_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    return line.lstrip("# ").strip()
    except OSError:
        pass
    return ""


FINDING_PATTERN = re.compile(r"\[(?P<status>.{1})\]")


def parse_findings(review_path: Path) -> FindingsSummary:
    summary = FindingsSummary()
    if not review_path.exists():
        return summary

    try:
        content = review_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return summary

    for match in FINDING_PATTERN.finditer(content):
        code = match.group("status")
        if code == " ":
            summary.open += 1
        elif code == "X":
            summary.claimed += 1
        elif code == "✓":
            summary.verified += 1
        elif code == "!":
            summary.regression += 1
        elif code == "~":
            summary.wont_fix += 1

    return summary


def determine_status(record: FeatureRecord) -> str:
    if not record.plan_exists:
        return "spec"
    if not record.tasks_exists:
        return "planning"
    if not record.review_exists:
        return "implementing"

    summary = record.findings
    if summary.regression > 0:
        return "regression"
    if summary.open > 0:
        return "reviewing"
    if summary.claimed > 0 and summary.verified == 0:
        return "fixing"
    if summary.open == 0 and summary.regression == 0 and summary.claimed == 0:
        return "verified"
    # Fall back to fixing if a mix remains
    return "fixing"


def gather_features(repo_root: Path) -> List[FeatureRecord]:
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []

    records: List[FeatureRecord] = []
    for feature_dir in sorted(d for d in specs_dir.iterdir() if d.is_dir()):
        feature_id = feature_dir.name
        spec_path = feature_dir / "spec.md"
        plan_path = feature_dir / "plan.md"
        tasks_path = feature_dir / "tasks.md"
        review_path = feature_dir / "review-findings.md"

        findings = parse_findings(review_path)

        existing_files = [p for p in [spec_path, plan_path, tasks_path, review_path] if p.exists()]
        last_update = None
        if existing_files:
            newest = max(existing_files, key=lambda p: p.stat().st_mtime)
            last_update = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc)

        record = FeatureRecord(
            feature_id=feature_id,
            title=read_spec_title(spec_path),
            status="",  # filled later
            spec_exists=spec_path.exists(),
            plan_exists=plan_path.exists(),
            tasks_exists=tasks_path.exists(),
            review_exists=review_path.exists(),
            findings=findings,
            last_updated=last_update,
            feature_dir=feature_dir.relative_to(repo_root),
        )
        record.status = determine_status(record)
        records.append(record)

    # Stable ordering: status progression then feature id
    records.sort(key=lambda rec: (STATUS_ORDER.get(rec.status, 99), rec.feature_id))
    return records


def isoformat(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_registry(repo_root: Path, records: Iterable[FeatureRecord]) -> Path:
    state_dir = repo_root / ".specify" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    registry_path = state_dir / "features.yaml"

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def dump_str(value: str) -> str:
        return json.dumps(value)

    with registry_path.open("w", encoding="utf-8") as handle:
        handle.write(f"generated_at: {generated_at}\n")
        handle.write("features:\n")
        for record in records:
            handle.write("  - id: " + dump_str(record.feature_id) + "\n")
            if record.title:
                handle.write("    title: " + dump_str(record.title) + "\n")
            handle.write("    status: " + dump_str(record.status) + "\n")
            handle.write("    artifacts:\n")
            handle.write("      spec: " + ("true" if record.spec_exists else "false") + "\n")
            handle.write("      plan: " + ("true" if record.plan_exists else "false") + "\n")
            handle.write("      tasks: " + ("true" if record.tasks_exists else "false") + "\n")
            handle.write("      review_findings: " + ("true" if record.review_exists else "false") + "\n")
            handle.write("    findings:\n")
            handle.write(f"      open: {record.findings.open}\n")
            handle.write(f"      claimed: {record.findings.claimed}\n")
            handle.write(f"      verified: {record.findings.verified}\n")
            handle.write(f"      regression: {record.findings.regression}\n")
            handle.write(f"      wont_fix: {record.findings.wont_fix}\n")
            handle.write("    paths:\n")
            handle.write("      root: " + dump_str(record.relative_path) + "\n")
            handle.write("      spec: " + dump_str((record.feature_dir / "spec.md").as_posix()) + "\n")
            handle.write("      plan: " + dump_str((record.feature_dir / "plan.md").as_posix()) + "\n")
            handle.write("      tasks: " + dump_str((record.feature_dir / "tasks.md").as_posix()) + "\n")
            handle.write("      review_findings: " + dump_str((record.feature_dir / "review-findings.md").as_posix()) + "\n")
            if record.last_updated:
                handle.write("    last_updated: " + dump_str(isoformat(record.last_updated)) + "\n")
    return registry_path


def print_table(records: List[FeatureRecord]) -> None:
    if not records:
        print("No features found. Use create-new-feature.sh to start a feature.")
        return

    header = f"{'Feature':<20} {'Status':<13} {'Open':>4} {'Claimed':>7} {'Verified':>8} {'Reg':>4} {'Updated':<20} Title"
    print(header)
    print("-" * len(header))
    for record in records:
        updated = isoformat(record.last_updated) or "-"
        print(
            f"{record.feature_id:<20} {record.status:<13} "
            f"{record.findings.open:>4} {record.findings.claimed:>7} {record.findings.verified:>8} {record.findings.regression:>4} "
            f"{updated:<20} {record.title}"
        )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise Spec Kit features and update the portfolio registry.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write .specify/state/features.yaml (diagnostic mode)",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Explicit repository root (defaults to auto-detection)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    start = Path.cwd()
    repo_root = find_repo_root(args.repo or start)

    records = gather_features(repo_root)
    if not args.no_write:
        write_registry(repo_root, records)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": repo_root.as_posix(),
        "features": [
            {
                "id": record.feature_id,
                "title": record.title,
                "status": record.status,
                "artifacts": {
                    "spec": record.spec_exists,
                    "plan": record.plan_exists,
                    "tasks": record.tasks_exists,
                    "review_findings": record.review_exists,
                },
                "findings": {
                    "open": record.findings.open,
                    "claimed": record.findings.claimed,
                    "verified": record.findings.verified,
                    "regression": record.findings.regression,
                    "wont_fix": record.findings.wont_fix,
                },
                "paths": {
                    "root": record.relative_path,
                    "spec": (record.feature_dir / "spec.md").as_posix(),
                    "plan": (record.feature_dir / "plan.md").as_posix(),
                    "tasks": (record.feature_dir / "tasks.md").as_posix(),
                    "review_findings": (record.feature_dir / "review-findings.md").as_posix(),
                },
                "last_updated": isoformat(record.last_updated),
            }
            for record in records
        ],
    }

    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print_table(records)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
