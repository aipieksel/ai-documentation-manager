---
name: project-documentation-updater
description: Maintain an established source-backed project documentation system under documents/documentation after focused source, configuration, workflow, or behavior changes. Use for bounded documentation maintenance, not initial adoption or comprehensive restructuring.
---

# Project Documentation Updater

Update the smallest accurate set of canonical documents after a bounded project change. This skill is portable and self-contained: resolve its scripts and references relative to this `SKILL.md`; do not copy it into the project or invoke another documentation workflow.

Invocation authorizes documentation and documentation-update evidence only. It does not authorize application-source changes, commits, pushes, deployments, paid services, or unrelated cleanup.

## Canonical contract

- Project knowledge: `documents/documentation/**`.
- Only routing index: `documents/documentation/0-index.md`.
- Current implementation docs: `documents/documentation/application/**`.
- High-level overview: `documents/documentation/project-overview.md`.
- Update evidence: `documents/tasks/documentation/update/YYYY-MM-DD-NNNNN-short-description/{ledger.json,audit.json}`.
- Never inspect or modify `documents/documentation/agents/` when that explicitly excluded private tree exists.

## Workflow

### 1. Prove the system is established

Read root and applicable nested `AGENTS.md`, then run:

```bash
python3 <SKILL_DIRECTORY>/scripts/prepare_update.py preflight \
  --project-root <PROJECT_ROOT>
```

Exit `2` means the structure is missing or incompatible. Stop and recommend `$project-documentation-builder`; do not perform a partial adoption.

### 2. Create one update record

```bash
python3 <SKILL_DIRECTORY>/scripts/prepare_update.py init \
  --project-root <PROJECT_ROOT> \
  --task "<TASK DESCRIPTION>"
```

Keep the returned `recordPath`, `ledgerPath`, and `auditPath`. Read [references/workflow.md](references/workflow.md) completely before writing.

### 3. Route and classify the whole change

- Inspect Git status/diff without claiming unrelated dirty changes.
- Route the user's exact request and every in-scope source/configuration/test path through `documents/documentation/0-index.md`.
- Read every routed document and authoritative source needed to check its claims.
- Record each path and decision in the ledger as `required`, `not-required`, `audit-only`, or `blocked`.
- Complete classification across the whole task before editing documentation.

### 4. Make the smallest accurate update

- Update existing owning documents instead of creating duplicates.
- Add a document only when the index and current documents prove no owner exists.
- Update the root index in the same run when a route, owner, or canonical path changes.
- Preserve accurate project-owned content, explicit status labels, and content outside managed `AGENTS.md` blocks.
- Do not refresh unrelated hashes, rewrite unrelated records, or broaden the task because the worktree is dirty.
- Escalate widespread ownership drift or structural incompatibility to `$project-documentation-builder`.

### 5. Validate evidence

Run the validator with the update record and every changed or explicitly checked documentation file:

```bash
python3 <SKILL_DIRECTORY>/scripts/validate_structure.py \
  --project-root <PROJECT_ROOT> \
  --mode task-scoped \
  --unrelated-ledger-policy warn \
  --ledger <LEDGER_PATH> \
  --audit <AUDIT_PATH> \
  --scope-path <DOCUMENTATION_PATH>
```

Exit `0` and an audit containing `"pass": true` are mandatory. A `not-required` result still needs path-specific evidence. For visible-UI claims, obey the project browser policy and prefer Ego Browser when available and authorized; do not require browser work for unrelated documentation.

## Completion

Report the impact classification, evidence inspected, documents changed, documents checked unchanged, index status, validator result, warnings/blockers, and exact record paths. Do not claim an update when the result was `not-required` or `audit-only`.
