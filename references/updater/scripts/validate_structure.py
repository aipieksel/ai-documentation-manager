#!/usr/bin/env python3
"""Validate the canonical single-index documentation structure.

This script uses only the Python standard library. Full mode enforces every
ledger and structure contract. Task-scoped mode keeps current-task documentation
strict while allowing unrelated historical ledger drift to be warned or ignored.
It intentionally ignores documents/documentation/agents/ contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote

SCHEMA = "documentation-structure-audit/v2"
LEDGER_SCHEMA = "documentation-reorganization-ledger/v2"

REQUIRED_INDEX_HEADINGS = [
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

REQUIRED_OVERVIEW_HEADINGS = [
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

ALLOWED_STATUSES = {
    "Current",
    "Implemented",
    "Supporting",
    "Needs Review",
    "Historical",
    "Planned",
    "Blocked",
}

ALLOWED_CLASSIFICATIONS = {
    "root-index",
    "documentation-entrypoint",
    "current-application",
    "project-overview",
    "operational",
    "historical",
    "observation",
    "navigation-only-index",
    "duplicate",
    "generated-scaffold",
    "excluded",
}

REQUIRED_PATHS = [
    "AGENTS.md",
    "documents/documentation/AGENTS.md",
    "documents/documentation/0-index.md",
    "documents/documentation/project-overview.md",
    "documents/documentation/application",
    "documents/documentation/agent-observations/anomalies.md",
    "documents/documentation/agent-observations/critical.md",
    "documents/documentation/agent-observations/recommendations.md",
    "documents/documentation/agent-observations/closed",
]

FORBIDDEN_PATHS = [
    "documents/documentation/index.md",
    "documents/documentation/search-index.json",
    "documents/documentation/search-keywords.md",
    "documents/documentation/source-context-map.md",
    "documents/documentation/documentation-workflow.md",
    "documents/documentation/templates",
    "documents/documentation/schemas",
    "documents/documentation/search",
    "documents/documentation/verification",
    "documents/documentation/documentation-system-tests",
    "documents/documentation/reports/documentation",
    "documents/documentation/preserved",
]

RESERVED_DOC_ROOT_ENTRIES = {
    "0-index.md",
    "project-overview.md",
    "AGENTS.md",
    "application",
    "agent-observations",
    "agents",
}

APPLICATION_LIKE_ROOTS = {
    "api", "apis", "architecture", "build", "build-deployment", "components",
    "configuration", "data", "deployment", "design", "features", "guides",
    "integrations", "maintenance", "modules", "reference", "state",
    "state-management", "ui", "ui-system", "workflows",
}

NESTED_INDEX_NAMES = {
    "0-index.md", "index.md", "search-index.md", "source-context-map.md",
}

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_rel(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def safe_project_relative(value: str) -> bool:
    if not value or value.startswith("/"):
        return False
    parts = PurePosixPath(value).parts
    return ".." not in parts and all(part not in {"", "."} for part in parts)


def heading_positions(text: str, headings: Iterable[str]) -> tuple[list[str], dict[str, int]]:
    found: list[str] = []
    positions: dict[str, int] = {}
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE):
        heading = match.group(1).strip()
        if heading in headings:
            found.append(heading)
            positions.setdefault(heading, match.start())
    return found, positions


def local_link_target(raw: str) -> str | None:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")]
    elif " " in value:
        value = value.split(" ", 1)[0]
    value = unquote(value.strip())
    if not value or value.startswith("#"):
        return None
    lower = value.lower()
    if lower.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
        return None
    return value.split("#", 1)[0].split("?", 1)[0]


def iter_current_markdown(doc_root: Path) -> Iterable[Path]:
    roots = [doc_root / "0-index.md", doc_root / "project-overview.md", doc_root / "AGENTS.md"]
    roots.extend(sorted((doc_root / "application").rglob("*.md")))
    roots.extend(sorted((doc_root / "agent-observations").glob("*.md")))
    for path in roots:
        if path.is_file():
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--mode", choices=("full", "task-scoped"), default="full")
    parser.add_argument(
        "--scope-path",
        action="append",
        default=[],
        help="Project-relative documentation path changed by the current task; repeat as needed.",
    )
    parser.add_argument(
        "--unrelated-ledger-policy",
        choices=("block", "warn", "ignore"),
        default=None,
        help="Failure policy for historical ledger entries outside --scope-path. Defaults to block in full mode and warn in task-scoped mode.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    ledger_path = Path(args.ledger).expanduser().resolve()
    audit_path = Path(args.audit).expanduser().resolve()
    doc_root = project_root / "documents/documentation"
    unrelated_ledger_policy = args.unrelated_ledger_policy or ("block" if args.mode == "full" else "warn")
    scope_paths: set[str] = set()
    for raw_scope in args.scope_path:
        normalized_scope = normalize_rel(str(raw_scope)).strip("/")
        if not safe_project_relative(normalized_scope):
            raise SystemExit(f"unsafe --scope-path: {raw_scope!r}")
        if not normalized_scope.startswith("documents/documentation/"):
            raise SystemExit(f"--scope-path must be inside documents/documentation/: {raw_scope!r}")
        scope_paths.add(normalized_scope)

    def in_scope(value: str) -> bool:
        normalized = normalize_rel(value).strip("/")
        return any(normalized == scope or normalized.startswith(scope + "/") or scope.startswith(normalized + "/") for scope in scope_paths)

    related_ledger_entries: set[int] = set()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []
    covered_documentation_paths: set[str] = set()

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail, "failurePolicy": "block"})

    check("project-root", project_root.is_dir(), str(project_root))

    for rel in REQUIRED_PATHS:
        path = project_root / rel
        check(f"required-path:{rel}", path.exists(), "exists" if path.exists() else "missing")

    for rel in FORBIDDEN_PATHS:
        path = project_root / rel
        check(f"forbidden-path:{rel}", not path.exists(), "absent" if not path.exists() else "present")

    ledger: dict[str, Any] = {}
    if not ledger_path.is_file():
        check("reorganization-ledger", False, f"missing: {ledger_path}")
    else:
        try:
            ledger = json.loads(read_text(ledger_path))
            check("reorganization-ledger-json", True, "valid JSON")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            check("reorganization-ledger-json", False, str(exc))

    operational_roots: set[str] = set()
    if ledger:
        check("ledger-schema", ledger.get("schema") == LEDGER_SCHEMA, str(ledger.get("schema")))
        check("ledger-mode", ledger.get("mode") in {"adopt", "restructure", "audit", "auto"}, repr(ledger.get("mode")))
        maintenance = ledger.get("maintenanceSchema") == "documentation-maintenance-ledger/v1"
        maintenance_impact = ledger.get("impact")
        if maintenance:
            check(
                "maintenance-impact",
                maintenance_impact in {"required", "not-required", "audit-only"},
                repr(maintenance_impact),
            )
            check("maintenance-task-wording", bool(str(ledger.get("taskWording", "")).strip()), repr(ledger.get("taskWording")))
            for field in ("inScopeSourcePaths", "sourceEvidence", "documentsChecked", "decisionEvidence"):
                value = ledger.get(field)
                check(f"maintenance-{field}", isinstance(value, list) and bool(value), repr(value))
            checked_documents = {
                normalize_rel(str(value)).strip("/")
                for value in ledger.get("documentsChecked", [])
                if isinstance(value, str)
            }
            check(
                "maintenance-scope-routed",
                all(scope in checked_documents for scope in scope_paths),
                f"scope={sorted(scope_paths)!r}; checked={sorted(checked_documents)!r}",
            )
        expected_order = [
            "inventory-and-classify",
            "finalize-path-map",
            "move-and-rename",
            "merge-and-remove-obsolete-indexes",
            "update-source-backed-content",
            "compile-root-index",
            "update-project-overview-and-agents",
            "validate",
        ]
        check("ledger-operation-order", ledger.get("orderedOperations") == expected_order, repr(ledger.get("orderedOperations")))
        check("ledger-index-updated", ledger.get("indexUpdated") is True, repr(ledger.get("indexUpdated")))
        check("ledger-index-finalized-after-moves", ledger.get("indexFinalizedAfterMoves") is True, repr(ledger.get("indexFinalizedAfterMoves")))
        check("ledger-substance-reviewed", ledger.get("substancePreservationReviewed") is True, repr(ledger.get("substancePreservationReviewed")))
        blocked = ledger.get("blockedItems")
        check("ledger-blocked-items", isinstance(blocked, list) and not blocked, repr(blocked))
        ignored = ledger.get("ignoredPaths")
        check("ledger-agents-exclusion", isinstance(ignored, list) and "documents/documentation/agents" in ignored, repr(ignored))

        raw_roots = ledger.get("operationalRoots", [])
        if not isinstance(raw_roots, list):
            check("ledger-operational-roots", False, "must be an array")
        else:
            for raw in raw_roots:
                if not isinstance(raw, str):
                    check("operational-root", False, f"non-string value {raw!r}")
                    continue
                normalized = normalize_rel(raw).strip("/")
                if normalized.startswith("documents/documentation/"):
                    normalized = normalized[len("documents/documentation/"):]
                valid = bool(normalized and "/" not in normalized and normalized not in RESERVED_DOC_ROOT_ENTRIES)
                valid = valid and normalized not in APPLICATION_LIKE_ROOTS and bool(KEBAB.fullmatch(normalized))
                check(f"operational-root:{raw}", valid, normalized)
                if valid:
                    operational_roots.add(normalized)

        entries = ledger.get("entries")
        if not isinstance(entries, list):
            check("ledger-entries", False, "must be an array")
        else:
            allowed_actions = {
                "created", "updated", "moved", "renamed", "moved-and-updated",
                "merged-and-removed", "removed-generated-scaffold", "unchanged",
            }
            for index, entry in enumerate(entries):
                prefix = f"ledger-entry:{index}"
                if not isinstance(entry, dict):
                    check(prefix, False, "entry must be an object")
                    continue
                action = entry.get("action")
                check(f"{prefix}:action", action in allowed_actions, repr(action))
                classification = entry.get("classification")
                check(f"{prefix}:classification", classification in ALLOWED_CLASSIFICATIONS, repr(classification))
                check(f"{prefix}:substance-disposition", bool(entry.get("substanceDisposition")), repr(entry.get("substanceDisposition")))

                before = normalize_rel(str(entry.get("beforePath", ""))) if entry.get("beforePath") else ""
                after = normalize_rel(str(entry.get("afterPath", ""))) if entry.get("afterPath") else ""
                if maintenance:
                    protected = any(
                        value == "documents/documentation/agents" or value.startswith("documents/documentation/agents/")
                        for value in (before, after)
                        if value
                    )
                    check(f"{prefix}:protected-agents-tree", not protected, f"{before} -> {after}")
                before_hash = str(entry.get("beforeSha256", ""))
                after_hash = str(entry.get("afterSha256", ""))
                if (before and in_scope(before)) or (after and in_scope(after)):
                    related_ledger_entries.add(index)
                safe_before = not before or safe_project_relative(before)
                safe_after = not after or safe_project_relative(after)
                check(f"{prefix}:before-path-safety", safe_before, before or "not supplied")
                check(f"{prefix}:after-path-safety", safe_after, after or "not supplied")

                for ledger_path_value in (before, after):
                    if ledger_path_value.startswith("documents/documentation/"):
                        covered_documentation_paths.add(ledger_path_value)

                if after.startswith("documents/documentation/application/"):
                    check(
                        f"{prefix}:application-classification",
                        classification in {"current-application", "historical"},
                        repr(classification),
                    )
                elif after.startswith("documents/documentation/agent-observations/"):
                    check(f"{prefix}:observation-classification", classification == "observation", repr(classification))
                elif after == "documents/documentation/project-overview.md":
                    check(f"{prefix}:overview-classification", classification == "project-overview", repr(classification))
                elif after.startswith("documents/documentation/") and after.count("/") >= 2:
                    root_name = after.split("/", 2)[1]
                    if root_name in operational_roots:
                        check(
                            f"{prefix}:operational-classification",
                            classification in {"operational", "historical"},
                            repr(classification),
                        )
                    elif classification == "current-application":
                        check(f"{prefix}:current-application-location", False, after)

                if action in {"moved", "renamed"}:
                    check(f"{prefix}:paths", bool(before and after and before != after), f"{before} -> {after}")
                    check(f"{prefix}:before-hash", bool(SHA256.fullmatch(before_hash)), before_hash)
                    check(f"{prefix}:after-hash", bool(SHA256.fullmatch(after_hash)), after_hash)
                    check(f"{prefix}:move-only-hash-match", before_hash == after_hash and bool(before_hash), f"{before_hash} / {after_hash}")
                    if before:
                        check(f"{prefix}:source-removed", safe_before and not (project_root / before).exists(), before)
                    after_path = project_root / after if safe_after else project_root / "__unsafe__"
                    check(f"{prefix}:destination", after_path.is_file(), str(after_path))
                    if after_path.is_file() and SHA256.fullmatch(after_hash):
                        check(f"{prefix}:destination-hash", sha256_file(after_path) == after_hash, after_hash)

                elif action == "moved-and-updated":
                    check(f"{prefix}:paths", bool(before and after and before != after), f"{before} -> {after}")
                    check(f"{prefix}:before-hash", bool(SHA256.fullmatch(before_hash)), before_hash)
                    check(f"{prefix}:after-hash", bool(SHA256.fullmatch(after_hash)), after_hash)
                    if before:
                        check(f"{prefix}:source-removed", safe_before and not (project_root / before).exists(), before)
                    after_path = project_root / after if after and safe_after else project_root / "__missing__"
                    check(f"{prefix}:destination", after_path.is_file(), str(after_path))
                    if after_path.is_file() and SHA256.fullmatch(after_hash):
                        check(f"{prefix}:destination-hash", sha256_file(after_path) == after_hash, after_hash)
                    authority = entry.get("sourceAuthority")
                    check(f"{prefix}:source-authority", isinstance(authority, list) and bool(authority), repr(authority))

                elif action == "updated":
                    check(f"{prefix}:paths", bool(before and after and before == after), f"{before} -> {after}")
                    check(f"{prefix}:before-hash", bool(SHA256.fullmatch(before_hash)), before_hash)
                    check(f"{prefix}:after-hash", bool(SHA256.fullmatch(after_hash)), after_hash)
                    after_path = project_root / after if after and safe_after else project_root / "__missing__"
                    check(f"{prefix}:destination", after_path.is_file(), str(after_path))
                    if after_path.is_file() and SHA256.fullmatch(after_hash):
                        check(f"{prefix}:destination-hash", sha256_file(after_path) == after_hash, after_hash)
                    authority = entry.get("sourceAuthority")
                    check(f"{prefix}:source-authority", isinstance(authority, list) and bool(authority), repr(authority))

                elif action in {"created", "unchanged"}:
                    check(f"{prefix}:after-path", bool(after), after)
                    after_path = project_root / after if after and safe_after else project_root / "__missing__"
                    check(f"{prefix}:destination", after_path.is_file(), str(after_path))
                    check(f"{prefix}:after-hash", bool(SHA256.fullmatch(after_hash)), after_hash)
                    if after_path.is_file() and SHA256.fullmatch(after_hash):
                        check(f"{prefix}:destination-hash", sha256_file(after_path) == after_hash, after_hash)

                elif action == "merged-and-removed":
                    check(f"{prefix}:before-path", bool(before), before)
                    if before:
                        check(f"{prefix}:source-removed", safe_before and not (project_root / before).exists(), before)
                    check(f"{prefix}:before-hash", bool(SHA256.fullmatch(before_hash)), before_hash)
                    preserved = entry.get("substancePreservedAt")
                    valid_preserved = isinstance(preserved, list) and bool(preserved)
                    check(f"{prefix}:preservation-destinations", valid_preserved, repr(preserved))
                    if valid_preserved:
                        for value in preserved:
                            preserved_rel = normalize_rel(str(value))
                            preserved_path = project_root / preserved_rel if safe_project_relative(preserved_rel) else project_root / "__unsafe__"
                            check(f"{prefix}:preserved:{value}", preserved_path.exists(), str(preserved_path))

                elif action == "removed-generated-scaffold":
                    check(f"{prefix}:before-path", bool(before), before)
                    if before:
                        check(f"{prefix}:source-removed", safe_before and not (project_root / before).exists(), before)
                    check(f"{prefix}:before-hash", bool(SHA256.fullmatch(before_hash)), before_hash)
                    check(f"{prefix}:evidence", bool(entry.get("generatedScaffoldEvidence")), repr(entry.get("generatedScaffoldEvidence")))

            if maintenance:
                actions = [entry.get("action") for entry in entries if isinstance(entry, dict)]
                if maintenance_impact == "required":
                    check(
                        "maintenance-required-has-change",
                        any(action != "unchanged" for action in actions),
                        repr(actions),
                    )
                elif maintenance_impact in {"not-required", "audit-only"}:
                    check(
                        "maintenance-no-change-actions",
                        bool(actions) and all(action == "unchanged" for action in actions),
                        repr(actions),
                    )

    if doc_root.is_dir():
        actual_root_entries = {p.name for p in doc_root.iterdir()}
        allowed_root_entries = RESERVED_DOC_ROOT_ENTRIES | operational_roots
        unexpected = sorted(actual_root_entries - allowed_root_entries)
        check("documentation-root-entries", not unexpected, repr(unexpected))

        for item in sorted(actual_root_entries - RESERVED_DOC_ROOT_ENTRIES):
            if item not in operational_roots:
                continue
            check(f"operational-root-exists:{item}", (doc_root / item).is_dir(), str(doc_root / item))

        nested_indexes: list[str] = []
        for path in doc_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(doc_root).as_posix()
            if rel == "0-index.md" or rel.startswith("agents/"):
                continue
            if path.name.lower() in NESTED_INDEX_NAMES:
                nested_indexes.append(rel)
        check("nested-index-files", not nested_indexes, repr(sorted(nested_indexes)))

        invalid_application_names: list[str] = []
        application_root = doc_root / "application"
        if application_root.is_dir():
            for path in application_root.rglob("*"):
                rel_parts = path.relative_to(application_root).parts
                for part in rel_parts[:-1] if path.is_file() else rel_parts:
                    if not KEBAB.fullmatch(part):
                        invalid_application_names.append(path.relative_to(doc_root).as_posix())
                        break
                if path.is_file() and path.suffix.lower() == ".md" and path.name != "README.md":
                    if not KEBAB.fullmatch(path.stem):
                        invalid_application_names.append(path.relative_to(doc_root).as_posix())
                if path.is_file() and path.suffix.lower() == ".md":
                    rel = path.relative_to(doc_root).as_posix()
                    try:
                        text = read_text(path)
                    except (OSError, UnicodeError) as exc:
                        check(f"application-metadata:{rel}:readable", False, str(exc))
                        continue
                    h1_count = len(re.findall(r"^#\s+", text, flags=re.MULTILINE))
                    status_match = re.search(r"^>\s*Status:\s*(.+?)\s*$", text, flags=re.MULTILINE)
                    updated_match = re.search(r"^>\s*Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", text, flags=re.MULTILINE)
                    status = status_match.group(1).strip() if status_match else ""
                    check(f"application-metadata:{rel}:single-h1", h1_count == 1, str(h1_count))
                    check(f"application-metadata:{rel}:status", status in ALLOWED_STATUSES, status or "missing")
                    check(f"application-metadata:{rel}:last-updated", bool(updated_match), updated_match.group(1) if updated_match else "missing")
                    check(f"application-metadata:{rel}:summary", bool(re.search(r"^##\s+Summary\s*$", text, flags=re.MULTILINE)), "present" if re.search(r"^##\s+Summary\s*$", text, flags=re.MULTILINE) else "missing")
                    source_heading = bool(re.search(r"^##\s+(Source Ownership|Source Context / Provenance|Maintenance Notes and Source References)\s*$", text, flags=re.MULTILINE))
                    check(f"application-metadata:{rel}:source-context", source_heading, "present" if source_heading else "missing")
                    verification_heading = bool(re.search(r"^##\s+Verification\s*$", text, flags=re.MULTILINE))
                    check(f"application-metadata:{rel}:verification", verification_heading, "present" if verification_heading else "missing")
        check("application-kebab-case", not invalid_application_names, repr(sorted(set(invalid_application_names))))

        current_documentation_files = sorted(
            path.relative_to(project_root).as_posix()
            for path in doc_root.rglob("*")
            if path.is_file() and not path.relative_to(doc_root).as_posix().startswith("agents/")
        )
        missing_ledger_coverage = [
            rel for rel in current_documentation_files if rel not in covered_documentation_paths
        ]
        missing_scope_coverage = [rel for rel in missing_ledger_coverage if in_scope(rel)]
        if args.mode == "task-scoped" and scope_paths:
            check("ledger-current-task-documentation-coverage", not missing_scope_coverage, repr(missing_scope_coverage[:200]))
        check("ledger-documentation-file-coverage", not missing_ledger_coverage, repr(missing_ledger_coverage[:200]))

    index_path = doc_root / "0-index.md"
    index_text = ""
    if index_path.is_file():
        try:
            index_text = read_text(index_path)
            check("root-index-readable", True, "UTF-8")
        except (OSError, UnicodeError) as exc:
            check("root-index-readable", False, str(exc))

    if index_text:
        h1_count = len(re.findall(r"^#\s+", index_text, flags=re.MULTILINE))
        status_match = re.search(r"^>\s*Status:\s*(.+?)\s*$", index_text, flags=re.MULTILINE)
        updated_match = re.search(r"^>\s*Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", index_text, flags=re.MULTILINE)
        status = status_match.group(1).strip() if status_match else ""
        check("root-index-single-h1", h1_count == 1, str(h1_count))
        check("root-index-status", status in ALLOWED_STATUSES, status or "missing")
        check("root-index-last-updated", bool(updated_match), updated_match.group(1) if updated_match else "missing")
        check("root-index-purpose", "> Purpose:" in index_text, "present" if "> Purpose:" in index_text else "missing")
        found, positions = heading_positions(index_text, REQUIRED_INDEX_HEADINGS)
        missing = [heading for heading in REQUIRED_INDEX_HEADINGS if heading not in positions]
        check("root-index-required-headings", not missing, repr(missing))
        ordered = [positions[h] for h in REQUIRED_INDEX_HEADINGS if h in positions]
        check("root-index-heading-order", len(ordered) == len(REQUIRED_INDEX_HEADINGS) and ordered == sorted(ordered), repr(found))
        for column in ["Search terms from the task or plan", "Primary documentation", "Source context to inspect", "Also read when relevant"]:
            check(f"root-index-column:{column}", column in index_text, "present" if column in index_text else "missing")
        agents_mentions = bool(re.search(r"documents/documentation/agents/|\]\(agents/", index_text))
        check("root-index-agents-exclusion", not agents_mentions, "not mentioned" if not agents_mentions else "mentioned")
        for root_name in sorted(operational_roots):
            check(f"root-index-operational-root:{root_name}", f"{root_name}/" in index_text, "mentioned" if f"{root_name}/" in index_text else "missing")

        missing_application_routes: list[str] = []
        application_root = doc_root / "application"
        if application_root.is_dir():
            for path in sorted(application_root.rglob("*.md")):
                rel = path.relative_to(doc_root).as_posix()
                if rel not in index_text:
                    missing_application_routes.append(rel)
        check("root-index-application-inventory", not missing_application_routes, repr(missing_application_routes))

        inventory_match = re.search(
            r"^## Application Documentation Inventory\s*$([\s\S]*?)(?=^##\s+|\Z)",
            index_text,
            flags=re.MULTILINE,
        )
        inventory_links: list[str] = []
        if inventory_match:
            for value in re.findall(r"\((application/[^)#?\s]+\.md)(?:#[^)]+)?\)", inventory_match.group(1)):
                if value not in inventory_links:
                    inventory_links.append(value)
        expected_inventory = sorted(
            [path.relative_to(doc_root).as_posix() for path in (doc_root / "application").rglob("*.md")]
            if (doc_root / "application").is_dir() else [],
            key=str.lower,
        )
        check(
            "root-index-application-inventory-order",
            inventory_links == expected_inventory,
            f"actual={inventory_links!r}; expected={expected_inventory!r}",
        )

    overview_path = doc_root / "project-overview.md"
    overview_text = ""
    if overview_path.is_file():
        try:
            overview_text = read_text(overview_path)
        except (OSError, UnicodeError) as exc:
            check("project-overview-readable", False, str(exc))
    if overview_text:
        h1_count = len(re.findall(r"^#\s+", overview_text, flags=re.MULTILINE))
        status_match = re.search(r"^>\s*Status:\s*(.+?)\s*$", overview_text, flags=re.MULTILINE)
        updated_match = re.search(r"^>\s*Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", overview_text, flags=re.MULTILINE)
        status = status_match.group(1).strip() if status_match else ""
        check("project-overview-single-h1", h1_count == 1, str(h1_count))
        check("project-overview-status", status in ALLOWED_STATUSES, status or "missing")
        check("project-overview-last-updated", bool(updated_match), updated_match.group(1) if updated_match else "missing")
        _, positions = heading_positions(overview_text, REQUIRED_OVERVIEW_HEADINGS)
        missing = [heading for heading in REQUIRED_OVERVIEW_HEADINGS if heading not in positions]
        check("project-overview-headings", not missing, repr(missing))
        agents_mentions = bool(re.search(r"documents/documentation/agents/|\]\(agents/", overview_text))
        check("project-overview-agents-exclusion", not agents_mentions, "not mentioned" if not agents_mentions else "mentioned")

    agents_path = project_root / "AGENTS.md"
    if agents_path.is_file():
        try:
            agents_text = read_text(agents_path)
            required_agents_strings = [
                "documents/documentation/0-index.md",
                "documents/documentation/project-overview.md",
                "documents/documentation/application/",
                "Folder-level index files MUST NOT be created.",
                "Every move, rename, addition, removal, or reorganization MUST update `documents/documentation/0-index.md` in the same run.",
                "BEGIN MANAGED BLOCK: agent-documentation-system",
                "END MANAGED BLOCK: agent-documentation-system",
            ]
            for value in required_agents_strings:
                check(f"agents-contract:{value}", value in agents_text, "present" if value in agents_text else "missing")
            start_count = agents_text.count("BEGIN MANAGED BLOCK: agent-documentation-system")
            end_count = agents_text.count("END MANAGED BLOCK: agent-documentation-system")
            check("agents-managed-block-count", start_count == 1 and end_count == 1, f"starts={start_count}; ends={end_count}")
            agents_tree_mentioned = bool(
                re.search(r"documents/documentation/agents/|\]\(documents/documentation/agents/", agents_text)
            )
            check(
                "agents-file-agents-tree-exclusion",
                not agents_tree_mentioned,
                "not mentioned" if not agents_tree_mentioned else "mentioned",
            )
        except (OSError, UnicodeError) as exc:
            check("agents-readable", False, str(exc))

    documentation_agents_path = doc_root / "AGENTS.md"
    if documentation_agents_path.is_file():
        try:
            documentation_agents_text = read_text(documentation_agents_path)
            required_documentation_agents_strings = [
                "0-index.md",
                "project-overview.md",
                "application/",
                "Authority Order",
                "Verification Contract",
                "Completion Check",
            ]
            for value in required_documentation_agents_strings:
                check(
                    f"documentation-agents-contract:{value}",
                    value in documentation_agents_text,
                    "present" if value in documentation_agents_text else "missing",
                )
            project_local_skill_dependency = bool(re.search(r"\.agents/skills/|\.agents/documentation-system/validate_structure\.py", documentation_agents_text))
            check(
                "documentation-agents-standalone",
                not project_local_skill_dependency,
                "no project-local runtime dependency" if not project_local_skill_dependency else "project-local runtime dependency found",
            )
        except (OSError, UnicodeError) as exc:
            check("documentation-agents-readable", False, str(exc))

    broken_links: list[str] = []
    for markdown_path in iter_current_markdown(doc_root) if doc_root.is_dir() else []:
        try:
            text = read_text(markdown_path)
        except (OSError, UnicodeError):
            continue
        for match in MARKDOWN_LINK.finditer(text):
            target = local_link_target(match.group(1))
            if target is None:
                continue
            candidate = (markdown_path.parent / target).resolve()
            try:
                candidate.relative_to(project_root)
            except ValueError:
                broken_links.append(f"{markdown_path.relative_to(project_root)} -> {target} (outside project)")
                continue
            if not candidate.exists():
                broken_links.append(f"{markdown_path.relative_to(project_root)} -> {target}")
    check("current-document-links", not broken_links, repr(broken_links[:100]))

    # Apply task-scoped failure policy only after every check is collected.
    # Current-task ledger entries and current-task coverage remain blocking.
    ledger_global_checks = {
        "reorganization-ledger",
        "reorganization-ledger-json",
        "ledger-schema",
        "ledger-operation-order",
        "ledger-index-updated",
        "ledger-index-finalized-after-moves",
        "ledger-substance-reviewed",
        "ledger-blocked-items",
        "ledger-agents-exclusion",
        "ledger-operational-roots",
        "ledger-entries",
        "ledger-documentation-file-coverage",
    }
    if args.mode == "task-scoped":
        for item in checks:
            if item["pass"]:
                continue
            name = str(item["name"])
            unrelated = False
            entry_match = re.match(r"^ledger-entry:(\d+)(?::|$)", name)
            if name.endswith(":protected-agents-tree"):
                unrelated = False
            elif entry_match:
                unrelated = int(entry_match.group(1)) not in related_ledger_entries
            elif name in ledger_global_checks:
                # Global historical-ledger completeness is current-task strict only
                # when this task actually changed documentation paths.
                unrelated = not scope_paths or name == "ledger-documentation-file-coverage"
            if unrelated:
                item["failurePolicy"] = unrelated_ledger_policy

    errors.clear()
    warnings.clear()
    for item in checks:
        if item["pass"]:
            continue
        rendered = f"{item['name']}: {item['detail']}"
        policy_name = str(item.get("failurePolicy", "block"))
        if policy_name == "warn":
            warnings.append(rendered)
        elif policy_name == "ignore":
            continue
        else:
            errors.append(rendered)

    audit = {
        "schema": SCHEMA,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "projectRoot": str(project_root),
        "ledger": str(ledger_path),
        "mode": args.mode,
        "scopePaths": sorted(scope_paths),
        "unrelatedLedgerPolicy": unrelated_ledger_policy,
        "pass": not errors,
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "operationalRoots": sorted(operational_roots),
        "checks": checks,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    if errors:
        print(f"Documentation structure validation failed with {len(errors)} error(s).", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(f"Audit: {audit_path}", file=sys.stderr)
        return 1

    if warnings:
        print(f"Documentation structure validation passed with {len(warnings)} warning(s).")
        for warning in warnings:
            print(f"- WARNING: {warning}")
    else:
        print("Documentation structure validation passed.")
    print(f"Audit: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
