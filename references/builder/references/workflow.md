# Documentation Organization Workflow — Hard Contract

This workflow governs documentation generation, adoption, reorganization, and maintenance. Every `MUST`, `MUST NOT`, gate, and ordered phase is mandatory. The workflow is incomplete until the structural validator passes.

## Canonical Output Contract

- Documentation root: `documentation`.
- `documents/documentation/0-index.md` is the only documentation routing index.
- Current implementation documentation MUST live under `documents/documentation/application/`.
- `documents/documentation/project-overview.md` MUST remain high-level.
- Unresolved findings MUST live under `documents/documentation/agent-observations/`.
- Verified operational records MAY remain in declared operational roots.
- `documents/documentation/AGENTS.md` is the mandatory documentation-folder entry point and MUST be validated as current documentation.
- `documents/documentation/agents/` is excluded and MUST remain untouched and unmentioned; do not confuse it with `documents/documentation/AGENTS.md`.
- Folder-level index files MUST NOT be created.
- Separate search indexes, keyword files, source-context maps, workflow pages, templates, schemas, reports, and generator tests MUST NOT be installed under `documents/documentation/`.
- Every move, rename, addition, removal, or reorganization MUST update `documents/documentation/0-index.md` in the same run.

## Authority Order

1. Current source, schemas, configuration, migrations, tests, and verified runtime behavior.
2. Current routed application documentation.
3. `documents/documentation/0-index.md` and `documents/documentation/project-overview.md`.
4. Current operational evidence.
5. Historical records and explicitly labeled inferences.

Generated output, old plans, screenshots, backups, and reports MUST NOT override current source authority.

## Phase 1 — Read and Inventory Gate

The agent MUST read applicable instruction files, project manifests, source entrypoints, tests, configuration, runtime data boundaries, and every documentation file except the excluded `documents/documentation/agents/` tree. The agent MUST inventory legacy roots and distinguish current application contracts from operational and historical records.

The agent MUST NOT write until the inventory identifies source authority for every current documentation domain.

## Phase 2 — Classification and Hash Gate

The agent MUST use `scripts/create_build_record.py` to create `documents/tasks/documentation/build/YYYY-MM-DD-NNNNN-short-description/{ledger.json,audit.json}` before any other documentation write. Every considered file MUST receive a classification and final disposition. Every moved, renamed, edited, merged, or removed file MUST have a before SHA-256.

`unknown` is not a final classification. An unresolved `unknown` MUST block the run.

## Phase 3 — Final Path Map Gate

The final path map MUST be complete before moves begin. Current implementation documentation MUST map to the narrowest accurate domain under `documents/documentation/application/`. Filenames and domain names MUST use lower-case kebab-case unless a substantive `README.md` is intentionally retained.

The path map MUST contain no collisions, duplicate canonical scopes, folder-level indexes, or operation inside `documents/documentation/agents/`.

## Phase 4 — Reorganization Gate

The agent MUST execute this order:

1. create target directories;
2. move/rename current application documents;
3. confirm move-only hashes remain identical;
4. repair only links and path references affected by moves;
5. merge unique index/source-routing substance;
6. place operational or historical records correctly;
7. remove obsolete indexes and generated scaffolding only after preservation proof;
8. remove empty obsolete directories;
9. update source-backed content only where necessary;
10. finalize after hashes and ledger dispositions.

Broad rewrites are forbidden when a move, rename, link correction, or focused update is sufficient. A moved file whose content must change MUST use the `moved-and-updated` ledger action with before and after hashes and source authority.

## Phase 5 — Root Index Gate

The root index MUST be compiled after final paths are stable. It MUST combine task-keyword routing and source-context routing. It MUST include the required headings from the bundled `schemas/documentation-index.schema.json`, link every application Markdown file, list every declared operational root, and omit the excluded agents tree.

The index MUST use real user/task wording, close aliases, primary documents, supporting documents, source paths, and verification routes. A document that is not reachable from the root index is not complete.

## Phase 6 — Overview and AGENTS Gate

The project overview MUST remain concise and project-wide. Detailed implementation content MUST be moved to the owning application document.

Root `AGENTS.md` MUST be the repository planning entry point and MUST preserve content outside the managed block. A project may also keep `documents/documentation/AGENTS.md` as the documentation-folder entry point. Both entry points MUST route to the same documentation root and task root, require index-first routing, source inspection, verification planning, substance preservation, and same-run index synchronization.

## Phase 7 — Maintenance Gate

For ongoing updates, the agent MUST route the user request and changed source paths through `documents/documentation/0-index.md`, update the smallest accurate document set, and update the index whenever routing or paths change. A new document without an index route is forbidden.

## Phase 8 — Validation Gate

The agent MUST re-read changed files, verify links and source paths, complete the ledger, and run:

```bash
python3 <SKILL_DIRECTORY>/scripts/validate_structure.py --project-root <PROJECT_ROOT> --mode full
```

Full adoption/reorganisation requires full mode. Ordinary task maintenance may use `--mode task-scoped`, repeated `--scope-path` values, and the configured unrelated-ledger policy. Exit code 0 is mandatory. Current-task failures must be repaired and rerun. Unrelated historical hash drift may be reported as a warning when configuration allows it and must not be "fixed" by refreshing another task's hashes. The agent MUST NOT report completion with a failed current-scope audit, missing current-task route, forbidden path introduced by the task, or unresolved current-task blocker.

## Preservation Contract

The agent MUST preserve documentation substance. A move-only file MUST remain byte-identical. A merged or removed file MUST identify where every unique accurate statement was preserved. A generated or navigation-only file MAY be removed only with evidence. User-authored content MUST NOT be silently deleted.

## Secret-Safety Contract

The agent MUST NOT copy credentials, tokens, cookies, private keys, private payloads, personal data, or sensitive identifiers into documentation or audits. Suspected secrets MUST be redacted before success.
