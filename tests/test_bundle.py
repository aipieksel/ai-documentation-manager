"""Check package preservation and relocated helpers without real project writes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".DS_Store", "__pycache__", ".git"}


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not any(part in IGNORED for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    }


class BundleTests(unittest.TestCase):
    def test_preserved_file_contents_and_inventory(self):
        manifest = json.loads((ROOT / "references/bundle-manifest.json").read_text())
        self.assertEqual(set(manifest["modules"]), {"builder", "updater"})
        for mode, module in manifest["modules"].items():
            with self.subTest(module=mode):
                renames = module["renamedFiles"]
                expected = {renames.get(name, name): value
                            for name, value in module["files"].items()}
                self.assertEqual(file_hashes(ROOT / "references" / mode), expected)
                self.assertEqual(renames, {"SKILL.md": "WORKFLOW.md"})

    def test_one_discoverable_skill_entrypoint(self):
        self.assertEqual(sorted(ROOT.rglob("SKILL.md")), [ROOT / "SKILL.md"])
        self.assertFalse(any(path.is_symlink() for path in ROOT.rglob("*")))

    def test_all_helpers_relocate_without_original_installations(self):
        with tempfile.TemporaryDirectory(prefix="aidm-relocation-") as temporary:
            root = Path(temporary)
            bundle = root / "Skill With Spaces"
            shutil.copytree(ROOT, bundle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for mode in ("builder", "updater"):
                for script in (bundle / "references" / mode / "scripts").glob("*.py"):
                    with self.subTest(script=script.name, mode=mode):
                        result = subprocess.run(
                            [sys.executable, "-B", str(script), "--help"],
                            cwd=root, capture_output=True, text=True, check=False,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)

    def test_update_rejects_fresh_or_legacy_project_without_mutation(self):
        with tempfile.TemporaryDirectory(prefix="aidm-preflight-") as temporary:
            root = Path(temporary)
            project = root / "Target With Spaces"
            project.mkdir()
            updater = ROOT / "references/updater/scripts/prepare_update.py"
            for state in ("fresh", "legacy"):
                if state == "legacy":
                    (project / "documentation").mkdir()
                    (project / "documentation/0-index.md").write_text("# Old index\n")
                before = file_hashes(project)
                before_paths = sorted(str(p.relative_to(project)) for p in project.rglob("*"))
                for command in ("preflight", "init"):
                    with self.subTest(state=state, command=command):
                        args = [sys.executable, "-B", str(updater), command,
                                "--project-root", str(project)]
                        if command == "init":
                            args += ["--task", "Update documentation"]
                        result = subprocess.run(args, cwd=root, capture_output=True, text=True)
                        self.assertEqual(result.returncode, 2, result.stderr)
                        self.assertEqual(json.loads(result.stderr)["status"], "blocked")
                        self.assertEqual(file_hashes(project), before)
                        self.assertEqual(
                            sorted(str(p.relative_to(project)) for p in project.rglob("*")),
                            before_paths,
                        )

    def test_builder_fixture_passes_relocated_updater_without_readoption(self):
        with tempfile.TemporaryDirectory(prefix="aidm-sequence-") as temporary:
            root = Path(temporary)
            bundle = root / "Only Installed Skill"
            shutil.copytree(ROOT, bundle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            fixture_path = bundle / "references/builder/scripts/tests/test_validate_structure.py"
            spec = importlib.util.spec_from_file_location("aidm_builder_fixture", fixture_path)
            fixture_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fixture_module)
            fixture = fixture_module.StandaloneValidatorTests()
            fixture.setUp()
            self.addCleanup(fixture.tearDown)
            self.assertEqual(fixture.run_validator().returncode, 0)
            project = fixture.project
            protected = project / "documents/documentation/agents/private.md"
            protected_before = protected.read_bytes()
            build_root = project / "documents/tasks/documentation/build"
            original_build = file_hashes(build_root)
            docs_before = file_hashes(project / "documents/documentation")
            updater = bundle / "references/updater/scripts/prepare_update.py"

            def run(script, *args):
                return subprocess.run(
                    [sys.executable, "-B", str(script), "--project-root", str(project), *args],
                    cwd=root, capture_output=True, text=True, check=False,
                )

            for command in ("preflight", "init"):
                args = [sys.executable, "-B", str(updater), command,
                        "--project-root", str(project)]
                if command == "init":
                    args += ["--task", "Verify existing runtime documentation"]
                result = subprocess.run(args, cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            paths = json.loads(result.stdout)
            ledger_path, audit_path = Path(paths["ledgerPath"]), Path(paths["auditPath"])
            doc_path = "documents/documentation/application/core.md"
            ledger = json.loads(ledger_path.read_text())
            ledger.update({
                "impact": "not-required",
                "inScopeSourcePaths": ["src/main.js"],
                "sourceEvidence": ["src/main.js"],
                "documentsChecked": [doc_path],
                "decisionEvidence": ["Source still exports ready=true; runtime claim unchanged."],
                "indexUpdated": True,
                "indexFinalizedAfterMoves": True,
                "substancePreservationReviewed": True,
                "entries": [{
                    "action": "unchanged",
                    "classification": "current-application",
                    "afterPath": doc_path,
                    "afterSha256": hashlib.sha256((project / doc_path).read_bytes()).hexdigest(),
                    "substanceDisposition": "Runtime claim still matches src/main.js.",
                    "sourceAuthority": ["src/main.js"],
                }],
            })
            ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
            def validate():
                return run(
                    bundle / "references/updater/scripts/validate_structure.py",
                    "--mode", "task-scoped", "--unrelated-ledger-policy", "warn",
                    "--ledger", str(ledger_path), "--audit", str(audit_path),
                    "--scope-path", doc_path,
                )

            # Preserve and expose the original initializer/validator mismatch.
            result = validate()
            self.assertNotEqual(result.returncode, 0)
            audit = json.loads(audit_path.read_text())
            self.assertEqual(
                [check["name"] for check in audit["checks"]
                 if not check["pass"] and check["failurePolicy"] == "block"],
                ["ledger-operation-order"],
            )
            self.assertEqual(
                [check["name"] for check in audit["checks"]
                 if not check["pass"] and check["failurePolicy"] == "warn"],
                ["ledger-documentation-file-coverage"],
            )
            ledger["orderedOperations"] = [
                "inventory-and-classify",
                "finalize-path-map",
                "move-and-rename",
                "merge-and-remove-obsolete-indexes",
                "update-source-backed-content",
                "compile-root-index",
                "update-project-overview-and-agents",
                "validate",
            ]
            ledger["decisionEvidence"].append(
                "Existing paths, index, overview and managed instructions remain valid. "
                "Move, merge and content-write stages require no changes for this fixture."
            )
            ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
            result = validate()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIs(json.loads(audit_path.read_text())["pass"], True)
            self.assertEqual(file_hashes(build_root), original_build)
            self.assertEqual(file_hashes(project / "documents/documentation"), docs_before)
            self.assertEqual(protected.read_bytes(), protected_before)
            self.assertFalse((project / ".agents/skills").exists())


if __name__ == "__main__":
    unittest.main()
