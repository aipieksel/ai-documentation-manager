# Documentation Maintenance Workflow

## 1. Establish Scope

Determine the project root from the active workspace. Read project instructions
and the canonical index before source inspection. Capture the current user's
request and the implementation work being closed out. Use `git status`, the
relevant diff, and conversation evidence to separate in-scope changes from
pre-existing or unrelated dirty paths. When ownership cannot be established,
classify the affected portion as `blocked` rather than claiming it.

Run preflight, then initialize a unique maintenance record before changing docs:

```bash
python3 <SKILL_DIRECTORY>/scripts/prepare_update.py init \
  --project-root <PROJECT_ROOT> \
  --task "<CONCISE CURRENT TASK>"
```

The command prints `recordPath`, `ledgerPath`, and `auditPath`. Preserve the original adoption
ledger. Never reuse or overwrite another maintenance ledger.

## 2. Route Before Editing

Search `documents/documentation/0-index.md` using:

- the user's exact nouns and verbs;
- feature, route, command, configuration, API, schema, migration, and workflow
  names from the current task;
- every in-scope changed source path and its stable parent ownership boundary;
- tests and verification artifacts that define durable behavior.

Read every primary and conditional route that matches. Then inspect the
authoritative changed source and enough neighboring code, tests, configuration,
or runtime evidence to evaluate the routed document's current claims. A Git diff
shows change, not full current behavior; read the resulting source where needed.

Finish routing and evidence collection for the entire task before editing any
documentation.

## 3. Classify Impact

Choose exactly one overall classification and record per-document decisions:

- `required`: durable behavior, interface, ownership, configuration, workflow,
  setup, verification, or source routing changed and a current doc must change;
- `not-required`: implementation changed but every routed durable claim remains
  accurate; record exact source paths, documents checked, and reasoning;
- `audit-only`: the invocation only checks documentation currency and no
  implementation change is in scope;
- `blocked`: missing authority, unresolved ownership, incompatible structure,
  or evidence prevents an accurate result.

Tests, refactors, generated files, lockfiles, formatting, and internal code can
still require docs when they alter a documented contract. Their filename or
change type alone never decides impact.

## 4. Populate the Maintenance Ledger

The initializer creates a validator-compatible ledger with additional
maintenance evidence fields. Before validation, set:

- `impact` to the final classification;
- `taskWording` to the user request being documented;
- `inScopeSourcePaths` to exact current-task paths only;
- `sourceEvidence` to source, diff, test, configuration, or runtime paths read;
- `documentsChecked` to every routed canonical document inspected;
- `decisionEvidence` to specific path-and-claim conclusions;
- `indexUpdated`, `indexFinalizedAfterMoves`, and
  `substancePreservationReviewed` to true only after checking them;
- `blockedItems` to unresolved blockers; validation requires it to be empty.

Add one validator entry for every changed or explicitly checked documentation
file. Use `updated`, `created`, or `unchanged` as appropriate. Include final
SHA-256 values, a concrete `substanceDisposition`, and `sourceAuthority` for
content edits. The validator's accepted classifications are structural:
`root-index` for `documents/documentation/0-index.md`, `documentation-entrypoint` for
`documents/documentation/AGENTS.md`, `current-application`, `project-overview`,
`operational`, `historical`, `observation`, and `generated-scaffold`. The
maintenance `impact` field is separate.

For an unchanged file, use:

```json
{
  "action": "unchanged",
  "classification": "current-application",
  "afterPath": "documents/documentation/application/example.md",
  "afterSha256": "<64 lower-case hex characters>",
  "substanceDisposition": "Checked documented behavior against src/example.ts; current claim remains accurate.",
  "sourceAuthority": ["src/example.ts"]
}
```

Do not include or inspect files beneath `documents/documentation/agents/`.

## 5. Make the Minimal Accurate Update

Update existing owning documents first. Create a new application document only
when no current document owns the durable contract and the index needs a stable
route. Keep metadata, source ownership, verification instructions, and status
accurate. Update `> Last updated:` only on documents whose substance changed.

Synchronize `documents/documentation/0-index.md` in the same run when a document path,
canonical ownership boundary, search term, source route, supporting route, or
verification route changed. Keep the application inventory sorted by final
path. Do not edit the index solely to mark that it was checked.

Moves and broad reorganization are exceptional in maintenance mode. If they
expand beyond a narrow current-task ownership correction, stop and invoke
`$project-documentation-builder` instead.

## 6. Validate and Report

Re-read changed documents through EOF. Verify links, source paths, headings,
metadata, current versus planned wording, and ledger hashes. Run task-scoped
validation using the unique ledger and audit paths. Pass every changed or
checked documentation path as `--scope-path`; this makes current-task ledger
coverage blocking while unrelated adoption-ledger drift remains a warning.

Do not repair unrelated warnings. A validation error, non-empty blocker list,
unresolved impact, missing current-task ledger entry, or touched protected agents
tree prevents success.
