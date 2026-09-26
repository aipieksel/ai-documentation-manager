# Documentation Structure Validation — Release Contract

The documentation run is releasable only when every mandatory check passes.

## Required Paths

- `AGENTS.md`
- `documents/documentation/0-index.md`
- `documents/documentation/project-overview.md`
- `documents/documentation/AGENTS.md` is the mandatory documentation-folder entry point
- `documents/documentation/application/`
- `documents/documentation/agent-observations/anomalies.md`
- `documents/documentation/agent-observations/critical.md`
- `documents/documentation/agent-observations/recommendations.md`
- `documents/tasks/documentation/build/YYYY-MM-DD-NNNNN-short-description/ledger.json`

## Single-Index Checks

- `documents/documentation/0-index.md` MUST be the only root or folder-level index.
- Folder-level index files MUST NOT be created.
- Every required index heading MUST exist in the required order.
- The keyword/source routing table MUST contain task wording, documentation routes, and source context.
- Every Markdown file under `documents/documentation/application/` MUST be linked from the root index.
- Every retained operational root MUST be declared in the ledger and described by the root index.

## Organization Checks

- Current implementation documentation MUST live under `documents/documentation/application/`.
- Additional documentation roots MUST be operational or historical, explicitly declared, and indexed as evidence rather than authority.
- Application paths MUST use stable lower-case kebab-case names, except an intentionally retained substantive `README.md`.
- `documents/documentation/AGENTS.md` is the mandatory documentation-folder entry point and is distinct from the excluded lowercase `documents/documentation/agents/` tree.
- `documents/documentation/agents/` MUST be ignored and MUST NOT be referenced by generated documentation.
- Forbidden generator scaffolding and duplicate root files MUST be absent.

## Preservation Checks

- Every move/rename ledger entry MUST contain before and after SHA-256 values.
- Move-only hashes MUST match.
- Every merged-and-removed entry MUST identify existing preservation destinations.
- Every removed generated scaffold MUST contain evidence that it was generated or navigation-only.
- Every updated file MUST have a verified after hash.
- `indexUpdated`, `indexFinalizedAfterMoves`, and `substancePreservationReviewed` MUST be true.


## Content and Duplication Checks

- Every application document MUST have exactly one H1, an allowed status, an ISO date, a Summary heading, source ownership/context, and a Verification heading.
- Root `AGENTS.md` MUST contain exactly one complete managed documentation block.
- `documents/documentation/AGENTS.md` MUST route through the canonical index without requiring project-local skills or a copied validator.
- The validator result MUST be supported by a completed classification ledger, not by filename inspection alone.
- Two current documents MUST NOT claim the same canonical ownership without explicit cross-linking and a clear primary contract.
- A navigation-only file MUST NOT survive merely because it contains links; its unique routing terms MUST be merged into the root index first.
- A substantive README MUST be retained or renamed according to its content, never removed by filename rule alone.
- Root-index inventory rows MUST be sorted by final application path so structural drift is visible during review.
- Generated audit artifacts MUST remain under `documents/tasks/documentation/build/` and MUST NOT become documentation routes.

## Link and Source Checks

- Current documentation links MUST resolve.
- Every referenced application document MUST exist.
- Current claims MUST be supported by source, configuration, tests, schemas, migrations, or verified runtime evidence.
- Planned and historical claims MUST be labeled accurately.

## Mechanical Gates

For installation, full adoption, audit, or reorganisation, run strict full validation:

```bash
python3 <SKILL_DIRECTORY>/scripts/validate_structure.py \
  --project-root <PROJECT_ROOT> --mode full \
  --ledger <CURRENT_BUILD_LEDGER> --audit <CURRENT_BUILD_AUDIT>
```

For ordinary task closeout, use scope-aware validation and pass each documentation file changed by that task:

```bash
python3 <SKILL_DIRECTORY>/scripts/validate_structure.py \
  --project-root <PROJECT_ROOT> \
  --mode task-scoped \
  --unrelated-ledger-policy warn \
  --ledger <CURRENT_BUILD_LEDGER> \
  --audit <CURRENT_BUILD_AUDIT> \
  --scope-path <CURRENT_TASK_DOCUMENTATION_PATH>
```

Both commands MUST exit 0 and write the current build record's `audit.json` with `"pass": true`. Full-mode errors block completion. Task-scoped current-task errors block completion; unrelated historical ledger drift may be a warning or ignored only when the task configuration explicitly permits it. The agent MUST NOT refresh unrelated hashes, overwrite another task's documentation, bypass current-scope validation, delete a failing check, or report success based on manual judgment alone.
