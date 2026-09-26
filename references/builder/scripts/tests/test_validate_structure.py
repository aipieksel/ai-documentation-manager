#!/usr/bin/env python3
"""Regression tests for the standalone documentation structure validator."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = SKILL_ROOT / "scripts/validate_structure.py"
SCAFFOLDS = SKILL_ROOT / "assets/scaffolds"

INDEX_HEADINGS = [
    "Required Routing Procedure",
    "Authority Order",
    "Status Legend",
    "Documentation Map",
    "Keyword and Source Routing Matrix",
    "Source-Path Router",
    "Cross-Cutting Planning Packs",
    "Application Documentation Inventory",
    "Operational and Historical Records",
    "Documentation Maintenance Rules",
    "Completion Check for Task Plans",
]

OVERVIEW_HEADINGS = [
    "Summary",
    "Users and Primary Outcomes",
    "Authority Order",
    "Stack and Runtime",
    "Implementation State",
    "Source Tree and Module Ownership",
    "Canonical End-to-End Flows",
    "Verification Approach",
    "Source Context / Provenance",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StandaloneValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="project-docs-builder-")
        self.project = Path(self.temporary.name)
        self._create_valid_project()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write(self, relative: str, content: str) -> Path:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _create_valid_project(self) -> None:
        block = (SCAFFOLDS / "root-agents-managed-block.md").read_text(encoding="utf-8")
        self._write("AGENTS.md", "# Fixture Rules\n\nKeep this project-owned line.\n\n" + block)
        shutil.copytree(SCAFFOLDS, self.project / "_scaffolds")
        self._write(
            "documents/documentation/AGENTS.md",
            (SCAFFOLDS / "documentation-agents.md").read_text(encoding="utf-8"),
        )
        for name in ("anomalies", "critical", "recommendations"):
            self._write(
                f"documents/documentation/agent-observations/{name}.md",
                (SCAFFOLDS / f"{name}.md").read_text(encoding="utf-8"),
            )
        (self.project / "documents/documentation/agent-observations/closed").mkdir(parents=True)
        self._write(
            "documents/documentation/application/core.md",
            "# Core Runtime\n\n"
            "> Status: Current\n"
            "> Last updated: 2026-09-05\n\n"
            "## Summary\n\nSource-backed runtime contract.\n\n"
            "## Source Ownership\n\n| Path | Responsibility |\n|---|---|\n| `src/main.js` | Runtime |\n\n"
            "## Verification\n\nRun the focused unit tests.\n",
        )
        overview = [
            "# Fixture Project Overview",
            "",
            "> Status: Current",
            "> Last updated: 2026-09-05",
            "",
        ]
        for heading in OVERVIEW_HEADINGS:
            overview.extend([f"## {heading}", "", "Verified fixture detail.", ""])
        self._write("documents/documentation/project-overview.md", "\n".join(overview))

        index = [
            "# Fixture Documentation Index",
            "",
            "> Status: Current",
            "> Last updated: 2026-09-05",
            "> Purpose: Route work to source-backed documentation.",
            "",
        ]
        for heading in INDEX_HEADINGS:
            index.extend([f"## {heading}", ""])
            if heading == "Keyword and Source Routing Matrix":
                index.extend([
                    "| Search terms from the task or plan | Primary documentation | Source context to inspect | Also read when relevant |",
                    "|---|---|---|---|",
                    "| core, runtime | [Core](application/core.md) | `src/main.js` | project overview |",
                    "",
                ])
            elif heading == "Application Documentation Inventory":
                index.extend([
                    "| File | Scope | Status |",
                    "|---|---|---|",
                    "| [application/core.md](application/core.md) | Runtime | Current |",
                    "",
                ])
        self._write("documents/documentation/0-index.md", "\n".join(index))
        self._write("src/main.js", "export const ready = true;\n")
        self._write("documents/documentation/agents/private.md", "EXCLUDED_SENTINEL\n")

        entries = []
        for path in sorted((self.project / "documents/documentation").rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(self.project).as_posix()
            if relative.startswith("documents/documentation/agents/"):
                continue
            if relative == "documents/documentation/0-index.md":
                classification = "root-index"
            elif relative == "documents/documentation/project-overview.md":
                classification = "project-overview"
            elif relative == "documents/documentation/AGENTS.md":
                classification = "documentation-entrypoint"
            elif relative.startswith("documents/documentation/application/"):
                classification = "current-application"
            else:
                classification = "observation"
            entries.append({
                "action": "created",
                "classification": classification,
                "substanceDisposition": "Created by fixture",
                "afterPath": relative,
                "afterSha256": digest(path),
            })
        ledger = {
            "schema": "documentation-reorganization-ledger/v2",
            "generatedAt": "2026-09-05T00:00:00Z",
            "projectRoot": str(self.project),
            "mode": "adopt",
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
            "entries": entries,
            "indexUpdated": True,
            "indexFinalizedAfterMoves": True,
            "substancePreservationReviewed": True,
            "blockedItems": [],
        }
        self._write(
            "documents/tasks/documentation/build/2026-09-05-00001-fixture/ledger.json",
            json.dumps(ledger, indent=2) + "\n",
        )
        shutil.rmtree(self.project / "_scaffolds")

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        record = self.project / "documents/tasks/documentation/build/2026-09-05-00001-fixture"
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--project-root", str(self.project), "--mode", "full",
             "--ledger", str(record / "ledger.json"), "--audit", str(record / "audit.json")],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_standalone_project_passes_without_installed_runtime(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / ".agents/skills").exists())
        self.assertFalse((self.project / ".agents/documentation-system/validate_structure.py").exists())
        self.assertEqual(
            (self.project / "documents/documentation/agents/private.md").read_text(encoding="utf-8"),
            "EXCLUDED_SENTINEL\n",
        )

    def test_invalid_application_metadata_is_blocking(self) -> None:
        path = self.project / "documents/documentation/application/core.md"
        path.write_text(path.read_text(encoding="utf-8").replace("> Status: Current\n", ""), encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("application-metadata:application/core.md:status", result.stderr)

    def test_duplicate_managed_block_is_blocking(self) -> None:
        path = self.project / "AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + (SCAFFOLDS / "root-agents-managed-block.md").read_text(encoding="utf-8"), encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agents-managed-block-count", result.stderr)

    def test_project_local_skill_dependency_is_blocking(self) -> None:
        path = self.project / "documents/documentation/AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nUse .agents/skills/update-documents/documentation/SKILL.md.\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("documentation-agents-standalone", result.stderr)


if __name__ == "__main__":
    unittest.main()
