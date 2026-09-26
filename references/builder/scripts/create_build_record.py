#!/usr/bin/env python3
"""Create a unique documentation-build record using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path("documents/tasks/documentation/build")
KINDS = ("adopt", "restructure", "audit")
DIR_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{5})-[a-z0-9][a-z0-9-]*$")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("title must contain at least one letter or number")
    return slug[:64].rstrip("-")


def next_number(root: Path, date: str) -> int:
    numbers = []
    if root.is_dir():
        for child in root.iterdir():
            match = DIR_PATTERN.fullmatch(child.name)
            if child.is_dir() and match and match.group(1) == date:
                numbers.append(int(match.group(2)))
    return max(numbers, default=0) + 1


def create_record(project_root: Path, title: str, mode: str) -> dict[str, str]:
    if not project_root.is_dir():
        raise ValueError(f"project root is not a directory: {project_root}")
    if mode not in KINDS:
        raise ValueError(f"mode must be one of: {', '.join(KINDS)}")

    now = datetime.now().astimezone()
    date = now.strftime("%Y-%m-%d")
    slug = slugify(title)
    records_root = project_root / ROOT
    records_root.mkdir(parents=True, exist_ok=True)

    number = next_number(records_root, date)
    while True:
        record = records_root / f"{date}-{number:05d}-{slug}"
        try:
            record.mkdir()
            break
        except FileExistsError:
            number += 1

    ledger_path = record / "ledger.json"
    audit_path = record / "audit.json"
    ledger = {
        "schema": "documentation-reorganization-ledger/v2",
        "generatedAt": now.isoformat(),
        "projectRoot": str(project_root),
        "mode": mode,
        "taskWording": title.strip(),
        "orderedOperations": [
            "inventory-and-classify",
            "finalize-path-map",
            "move-and-rename",
            "merge-and-remove-obsolete-indexes",
            "update-source-backed-content",
            "compile-root-index",
            "update-project-overview-and-agents",
            "validate",
        ],
        "operationalRoots": [],
        "ignoredPaths": ["documents/documentation/agents"],
        "entries": [],
        "indexUpdated": False,
        "indexFinalizedAfterMoves": False,
        "substancePreservationReviewed": False,
        "blockedItems": [],
    }
    audit = {
        "schema": "documentation-structure-audit/v2",
        "generatedAt": now.isoformat(),
        "status": "pending",
        "pass": False,
        "checks": [],
    }
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "initialized",
        "recordPath": str(record),
        "ledgerPath": str(ledger_path),
        "auditPath": str(audit_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--mode", choices=KINDS, default="restructure")
    args = parser.parse_args()
    try:
        result = create_record(
            Path(args.project_root).expanduser().resolve(), args.title, args.mode
        )
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
