from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "create_build_record.py"


class CreateBuildRecordTests(unittest.TestCase):
    def run_script(self, root: Path, title: str = "Build project docs"):
        return subprocess.run(
            ["python3", str(SCRIPT), "--project-root", str(root), "--title", title, "--mode", "adopt"],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_creates_populated_record_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self.run_script(root)
            second = self.run_script(root)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            one = json.loads(first.stdout)
            two = json.loads(second.stdout)
            self.assertNotEqual(one["recordPath"], two["recordPath"])
            self.assertRegex(Path(one["recordPath"]).name, r"^\d{4}-\d{2}-\d{2}-\d{5}-build-project-docs$")
            self.assertTrue(Path(one["ledgerPath"]).is_file())
            self.assertTrue(Path(one["auditPath"]).is_file())
            self.assertEqual(json.loads(Path(one["ledgerPath"]).read_text())["mode"], "adopt")

    def test_rejects_empty_slug(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_script(Path(temporary), "---")
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
