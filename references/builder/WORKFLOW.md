---
name: project-documentation-builder
description: Build, adopt, or comprehensively reorganize a software project's documentation into a source-backed single-index system under documents/documentation. Use for initial documentation systems and full documentation restructuring, not narrow maintenance updates.
---

# Project Documentation Builder

Create a complete, maintainable documentation system from current project evidence. The skill is portable and self-contained: resolve all scripts, references, schemas, templates, and scaffolds relative to this `SKILL.md`. Do not install project-local copies of the skill or depend on sibling skills.

Invocation authorizes documentation, documentation-routing, managed `AGENTS.md` blocks, and task evidence for this bounded workflow. It does not authorize application-source changes, commits, pushes, deployments, paid services, or deletion of unclassified substantive content.

## Canonical output

```text
documents/
├── documentation/
│   ├── 0-index.md
│   ├── project-overview.md
│   ├── AGENTS.md
│   ├── application/
│   └── agent-observations/
└── tasks/
    └── documentation/
        └── build/
            └── YYYY-MM-DD-NNNNN-short-description/
                ├── ledger.json
                └── audit.json
```

- `documents/documentation/0-index.md` is the only documentation routing and source-context index.
- Current implementation contracts live under `documents/documentation/application/`.
- `project-overview.md` stays high-level.
- Unresolved findings live under `agent-observations/`.
- Build records are operational evidence under `documents/tasks/`; they are never current product documentation.
- Keep the repository-root `README.md`; do not use README files as competing documentation indexes.
- Never inspect or modify `documents/documentation/agents/` if that explicitly excluded private tree exists.

## Bundled resources

Before writing:

1. Read [references/workflow.md](references/workflow.md).
2. Read [references/validation-contract.md](references/validation-contract.md).
3. Use the schemas under `references/schemas/`.
4. Use `assets/templates/` and `assets/scaffolds/` as shape references, replacing every placeholder from project evidence.
5. Use `scripts/create_build_record.py` to allocate the build record.
6. Use `scripts/validate_structure.py` for final validation.

Do not copy these resources into the target project.

## Workflow

### 1. Establish authority and recovery

- Resolve the exact project root and read every applicable `AGENTS.md` before project inspection.
- Read the root README, manifests, documentation entry points, source entry points, configuration, schemas/migrations, tests, scripts, and runtime/deployment boundaries relevant to accurate documentation.
- Inspect Git status and preserve unrelated work. If the workflow will move or remove existing documentation, create the recovery checkpoint required by project policy before mutation.
- Treat current source, configuration, schemas, tests, and verified runtime behavior as stronger evidence than old docs, plans, screenshots, generated reports, or prior conversations.

### 2. Create the build record first

Run:

```bash
python3 <SKILL_DIRECTORY>/scripts/create_build_record.py \
  --project-root <PROJECT_ROOT> \
  --title "<TASK DESCRIPTION>" \
  --mode <adopt|restructure|audit>
```

Record the returned `recordPath`, `ledgerPath`, and `auditPath`. Populate the ledger before any other documentation or managed-`AGENTS.md` write. Every considered document needs a classification, source authority, disposition, and final path. Every move, edit, merge, or removal needs a before hash. An unresolved classification blocks mutation.

### 3. Inventory and map before moving

- Inventory existing documentation roots without traversing the excluded private agents tree.
- Distinguish current contracts from tasks, research, audits, reports, logs, screenshots, backups, and historical evidence.
- Map current contracts to lower-case kebab-case paths under `documents/documentation/application/`.
- Preserve task and operational material under an appropriate `documents/tasks/**` namespace; research, reports, audits, and archives belong in their canonical `documents/*` categories.
- Resolve collisions, duplicate ownership, nested indexes, and broken routes before executing moves.

### 4. Reorganize without losing substance

Execute coherent operations in this order:

1. create required destinations;
2. move/rename documents using Git-aware moves when available;
3. verify byte-identical hashes for move-only files;
4. repair links made stale by moves;
5. merge unique routing/source-context substance from obsolete indexes;
6. classify operational and historical records;
7. remove obsolete navigation/generated scaffolding only after preservation is proven;
8. remove empty obsolete roots;
9. write or update source-backed application documents;
10. finalize hashes and ledger dispositions.

Focused moves and edits are preferred to broad rewrites. Never delete substantive user-authored documentation based only on filename, age, or duplication heuristics.

### 5. Build routing and entry points

Compile `documents/documentation/0-index.md` only after final paths are stable. It must route real task wording and source paths to primary documents, supporting documents, and verification context, and link every current application document.

Keep `project-overview.md` concise and project-wide. Insert or replace exactly one managed documentation block in root `AGENTS.md`, preserving all content outside its markers. Create or update `documents/documentation/AGENTS.md` as the folder-local entry point without introducing project-local skill dependencies.

### 6. Validate and verify

Re-read every changed file through EOF; check links, source paths, current/planned labels, hashes, ledger completeness, and secret safety. Then run:

```bash
python3 <SKILL_DIRECTORY>/scripts/validate_structure.py \
  --project-root <PROJECT_ROOT> \
  --mode full \
  --ledger <LEDGER_PATH> \
  --audit <AUDIT_PATH>
```

Exit `0` and an audit with `"pass": true` are mandatory. Repair and rerun current-scope failures. When documentation claims depend on visible UI behavior, follow the project's browser policy; prefer Ego Browser when it is available and authorized, but do not make it a dependency for non-browser documentation work.

## Completion

Report the documentation root, application-document count, moves/renames/merges, retired legacy roots, operational roots retained, root-index synchronization, validation result, blockers, and exact build-record paths. Report only observed evidence; do not claim runtime or browser verification that was not performed.
