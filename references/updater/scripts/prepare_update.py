#!/usr/bin/env python3
"""Preflight canonical documentation and initialize a unique update record."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


BEGIN = "<!-- BEGIN MANAGED BLOCK: agent-documentation-system -->"
END = "<!-- END MANAGED BLOCK: agent-documentation-system -->"
ROOT = Path("documents/tasks/documentation/update")
DIR_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{5})-[a-z0-9][a-z0-9-]*$")


def canonical_missing(project_root: Path) -> list[str]:
    required = [
        "AGENTS.md",
        "documents/documentation/0-index.md",
        "documents/documentation/project-overview.md",
        "documents/documentation/AGENTS.md",
        "documents/documentation/application",
    ]
    missing = [rel for rel in required if not (project_root / rel).exists()]
    agents = project_root / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            missing.append("AGENTS.md managed documentation block")
    return missing


def fail_preflight(project_root: Path, missing: list[str]) -> int:
    print(json.dumps({
        "status": "blocked", "projectRoot": str(project_root),
        "missingOrIncompatible": missing,
        "instruction": "Run $project-documentation-builder before $project-documentation-updater.",
    }, indent=2), file=sys.stderr)
    return 2


def preflight(project_root: Path, *, emit_success: bool = True) -> int:
    if not project_root.is_dir():
        return fail_preflight(project_root, ["project root"])
    try:
        missing = canonical_missing(project_root)
    except (OSError, UnicodeError) as exc:
        print(f"Unable to read canonical documentation structure: {exc}", file=sys.stderr)
        return 2
    if missing:
        return fail_preflight(project_root, missing)
    if emit_success:
        print(json.dumps({"status": "ready", "projectRoot": str(project_root)}, indent=2))
    return 0


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("task must contain at least one letter or number")
    return slug[:64].rstrip("-")


def next_number(root: Path, date: str) -> int:
    numbers = []
    if root.is_dir():
        for child in root.iterdir():
            match = DIR_PATTERN.fullmatch(child.name)
            if child.is_dir() and match and match.group(1) == date:
                numbers.append(int(match.group(2)))
    return max(numbers, default=0) + 1


def initialize(project_root: Path, task: str) -> int:
    if preflight(project_root, emit_success=False):
        return 2
    try:
        slug = slugify(task)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    now = datetime.now().astimezone()
    date = now.strftime("%Y-%m-%d")
    root = project_root / ROOT
    root.mkdir(parents=True, exist_ok=True)
    number = next_number(root, date)
    while True:
        record = root / f"{date}-{number:05d}-{slug}"
        try:
            record.mkdir()
            break
        except FileExistsError:
            number += 1
    ledger_path = record / "ledger.json"
    audit_path = record / "audit.json"
    ledger = {
        "schema": "documentation-reorganization-ledger/v2",
        "maintenanceSchema": "documentation-maintenance-ledger/v1",
        "generatedAt": now.isoformat(), "projectRoot": str(project_root),
        "mode": "audit", "taskWording": task.strip(), "impact": "pending",
        "inScopeSourcePaths": [], "sourceEvidence": [], "documentsChecked": [],
        "decisionEvidence": [],
        "orderedOperations": ["route", "classify", "update", "synchronize-index", "validate"],
        "operationalRoots": [], "ignoredPaths": ["documents/documentation/agents"],
        "entries": [], "indexUpdated": False, "indexFinalizedAfterMoves": False,
        "substancePreservationReviewed": False, "blockedItems": [],
    }
    audit = {
        "schema": "documentation-structure-audit/v2", "generatedAt": now.isoformat(),
        "status": "pending", "pass": False, "checks": [],
    }
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "initialized", "projectRoot": str(project_root),
        "recordPath": str(record), "ledgerPath": str(ledger_path),
        "auditPath": str(audit_path),
    }, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "init"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--project-root", required=True)
        if command == "init":
            sub.add_argument("--task", required=True)
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    return preflight(project_root) if args.command == "preflight" else initialize(project_root, args.task)


if __name__ == "__main__":
    raise SystemExit(main())
