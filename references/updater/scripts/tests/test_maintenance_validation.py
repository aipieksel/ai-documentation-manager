#!/usr/bin/env python3
"""Regression tests for task-scoped documentation maintenance validation."""
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
SCAFFOLDS = Path(__file__).resolve().parent / "fixtures"

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


class MaintenanceValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="one-shot-docs-")
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
            "documents/tasks/documentation/update/2026-09-05-00001-fixture/ledger.json",
            json.dumps(ledger, indent=2) + "\n",
        )
        shutil.rmtree(self.project / "_scaffolds")

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        record = self.project / "documents/tasks/documentation/update/2026-09-05-00001-fixture"
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--project-root", str(self.project), "--mode", "full",
             "--ledger", str(record / "ledger.json"), "--audit", str(record / "audit.json")],
            capture_output=True,
            text=True,
            check=False,
        )

    def write_maintenance_ledger(
        self,
        *,
        impact: str,
        action: str = "unchanged",
        before_hash: str = "",
        evidence: bool = True,
        extra_entries: list[dict[str, object]] | None = None,
    ) -> tuple[Path, Path]:
        document = self.project / "documents/documentation/application/core.md"
        entry: dict[str, object] = {
            "action": action,
            "classification": "current-application",
            "substanceDisposition": "Checked the runtime contract against src/main.js.",
            "afterPath": "documents/documentation/application/core.md",
            "afterSha256": digest(document),
            "sourceAuthority": ["src/main.js"],
        }
        if action == "updated":
            entry["beforePath"] = "documents/documentation/application/core.md"
            entry["beforeSha256"] = before_hash
        entries = [entry, *(extra_entries or [])]
        ledger = {
            "schema": "documentation-reorganization-ledger/v2",
            "generatedAt": "2026-09-05T00:00:00Z",
            "projectRoot": str(self.project),
            "mode": "audit",
            "maintenanceSchema": "documentation-maintenance-ledger/v1",
            "taskWording": "Maintain runtime documentation",
            "impact": impact,
            "inScopeSourcePaths": ["src/main.js"] if evidence else [],
            "sourceEvidence": ["src/main.js"] if evidence else [],
            "documentsChecked": ["documents/documentation/application/core.md"] if evidence else [],
            "decisionEvidence": ["Core runtime claim checked against src/main.js"] if evidence else [],
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
        ledger_path = self.project / "documents/tasks/documentation/update/task-ledger.json"
        audit_path = self.project / "documents/tasks/documentation/update/task-audit.json"
        self._write(ledger_path.relative_to(self.project).as_posix(), json.dumps(ledger, indent=2) + "\n")
        return ledger_path, audit_path

    def run_maintenance_validator(self, ledger: Path, audit: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--project-root",
                str(self.project),
                "--mode",
                "task-scoped",
                "--unrelated-ledger-policy",
                "warn",
                "--ledger",
                str(ledger),
                "--audit",
                str(audit),
                "--scope-path",
                "documents/documentation/application/core.md",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_required_update_passes_with_source_backed_entry(self) -> None:
        document = self.project / "documents/documentation/application/core.md"
        before_hash = digest(document)
        document.write_text(document.read_text().replace("Source-backed", "Updated source-backed"), encoding="utf-8")
        ledger, audit = self.write_maintenance_ledger(
            impact="required", action="updated", before_hash=before_hash
        )
        result = self.run_maintenance_validator(ledger, audit)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(audit.read_text())["pass"])

    def test_root_index_and_documentation_entrypoint_classifications_pass(self) -> None:
        index = self.project / "documents/documentation/0-index.md"
        instructions = self.project / "documents/documentation/AGENTS.md"
        extra_entries = [
            {
                "action": "unchanged",
                "classification": "root-index",
                "substanceDisposition": "Routing remains accurate.",
                "afterPath": "documents/documentation/0-index.md",
                "afterSha256": digest(index),
            },
            {
                "action": "unchanged",
                "classification": "documentation-entrypoint",
                "substanceDisposition": "Instructions remain accurate.",
                "afterPath": "documents/documentation/AGENTS.md",
                "afterSha256": digest(instructions),
            },
        ]
        ledger, audit = self.write_maintenance_ledger(
            impact="not-required", extra_entries=extra_entries
        )
        payload = json.loads(ledger.read_text())
        payload["documentsChecked"].extend(
            ["documents/documentation/0-index.md", "documents/documentation/AGENTS.md"]
        )
        ledger.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        result = self.run_maintenance_validator(ledger, audit)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_not_required_result_passes_with_exact_evidence(self) -> None:
        ledger, audit = self.write_maintenance_ledger(impact="not-required")
        result = self.run_maintenance_validator(ledger, audit)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_not_required_without_evidence_is_blocking(self) -> None:
        ledger, audit = self.write_maintenance_ledger(impact="not-required", evidence=False)
        result = self.run_maintenance_validator(ledger, audit)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("maintenance-sourceEvidence", result.stderr)

    def test_unrelated_dirty_source_is_ignored(self) -> None:
        self._write("src/unrelated.js", "export const unrelated = true;\n")
        ledger, audit = self.write_maintenance_ledger(impact="not-required")
        result = self.run_maintenance_validator(ledger, audit)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_protected_agents_tree_entry_is_always_blocking(self) -> None:
        private = self.project / "documents/documentation/agents/private.md"
        protected_entry = {
            "action": "unchanged",
            "classification": "historical",
            "substanceDisposition": "Should never be inspected.",
            "afterPath": "documents/documentation/agents/private.md",
            "afterSha256": digest(private),
        }
        ledger, audit = self.write_maintenance_ledger(
            impact="not-required", extra_entries=[protected_entry]
        )
        result = self.run_maintenance_validator(ledger, audit)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("protected-agents-tree", result.stderr)

    def test_current_scope_structure_failure_is_blocking(self) -> None:
        document = self.project / "documents/documentation/application/core.md"
        document.write_text(document.read_text().replace("> Status: Current\n", ""), encoding="utf-8")
        ledger, audit = self.write_maintenance_ledger(impact="not-required")
        result = self.run_maintenance_validator(ledger, audit)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("application-metadata:application/core.md:status", result.stderr)

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
