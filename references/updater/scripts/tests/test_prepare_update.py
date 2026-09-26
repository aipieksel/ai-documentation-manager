from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "prepare_update.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", str(SCRIPT), *args], text=True, capture_output=True, check=False)


def adopted_project(root: Path) -> None:
    (root / "documents/documentation/application").mkdir(parents=True)
    (root / "documents/documentation/0-index.md").write_text("# Index\n", encoding="utf-8")
    (root / "documents/documentation/project-overview.md").write_text("# Overview\n", encoding="utf-8")
    (root / "documents/documentation/AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
    (root / "AGENTS.md").write_text(
        "before\n<!-- BEGIN MANAGED BLOCK: agent-documentation-system -->\n"
        "managed\n<!-- END MANAGED BLOCK: agent-documentation-system -->\nafter\n",
        encoding="utf-8",
    )


class PrepareUpdateTests(unittest.TestCase):
    def test_preflight_accepts_adopted_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adopted_project(root)
            result = run("preflight", "--project-root", str(root))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "ready")

    def test_preflight_blocks_missing_prerequisite_with_exact_remedy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run("preflight", "--project-root", temporary)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stderr)
            self.assertIn("$project-documentation-builder", payload["instruction"])
            self.assertIn("documents/documentation/0-index.md", payload["missingOrIncompatible"])

    def test_init_creates_unique_dated_records_without_touching_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adopted_project(root)
            doc_root = root / "documents/documentation"
            before = {p.relative_to(doc_root): p.read_bytes() for p in doc_root.rglob("*") if p.is_file()}
            first = run("init", "--project-root", str(root), "--task", "Update API docs")
            second = run("init", "--project-root", str(root), "--task", "Update API docs")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            one = json.loads(first.stdout)
            two = json.loads(second.stdout)
            self.assertNotEqual(one["recordPath"], two["recordPath"])
            self.assertRegex(Path(one["recordPath"]).name, r"^\d{4}-\d{2}-\d{2}-\d{5}-update-api-docs$")
            ledger = json.loads(Path(one["ledgerPath"]).read_text())
            self.assertEqual(ledger["impact"], "pending")
            self.assertTrue(Path(one["auditPath"]).is_file())
            after = {p.relative_to(doc_root): p.read_bytes() for p in doc_root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
