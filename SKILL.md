---
name: ai-documentation-manager
description: Build or update source-backed project documentation with one entrypoint. Use build for one-shot adoption or full restructuring and update for bounded maintenance after the documentation system is established. Accept an optional project folder; otherwise use the current project root. Composer shorthand AIDM.
---

# AI Documentation Manager

Route to one of two preserved documentation packages. This entrypoint changes invocation and target selection only; it does not merge, replace or relax either package's workflow, scripts, schemas, preservation rules or validation gates.

## Invocation

Canonical invocation: `$ai-documentation-manager`.

In the Codex composer, type `/aidm`, select **AI Documentation Manager** and press Tab, then append the mode and optional project folder. This is skill selection, like `/aidw` for AI Development Workflow, not a registered slash-command alias. If the shorthand is not suggested by the client, select the full skill name or use the canonical invocation. Plain `@aidm` or `$aidm` text is not the canonical skill attachment.

```text
$ai-documentation-manager build
$ai-documentation-manager build /path/to/project
$ai-documentation-manager build "/path with spaces/project"
$ai-documentation-manager update
$ai-documentation-manager update /path/to/project
```

Accept `build` and `update` case-insensitively. A clear natural-language request for one mode may select it. With neither mode nor an unambiguous request, ask which operation is intended before writing. Do not import numeric development stages, automatically run both modes, or infer a build merely because update preflight fails.

### Select the target once

- An optional folder after the mode identifies the target project, not the skill package. A linked `SKILL.md` in the invocation identifies the skill instructions only.
- Expand `~/` using the user's home and resolve relative paths against the chat's original working directory. Support quoted paths containing spaces; treat paths as literal filesystem data, never executable shell text.
- An explicit folder overrides chat cwd and previously discussed projects. Verify it exists and identifies one project root; never silently fall back to another project if it is invalid or ambiguous.
- Without a folder, use the current project's root as established by the workspace and its instructions. Do not use the skill's installation directory or automatically replace a documented subproject root with a monorepo root. Ask only when the root cannot be established reliably.
- State the selected mode and absolute project root briefly, read its applicable `AGENTS.md` and documentation, and carry that same target through the module. No repeat target approval is needed for an unambiguous request.
- Run project-relative investigation from the selected project root and supply its absolute path to every helper's `--project-root`. Changing cwd to read a skill resource must not change the target.
- A request to edit this skill containing example invocations does not authorize documentation generation in those example projects.

## Route to the preserved package

| Mode | Read in full | Resource base |
|---|---|---|
| `build` | [Builder instructions](references/builder/WORKFLOW.md) | `references/builder/` |
| `update` | [Updater instructions](references/updater/WORKFLOW.md) | `references/updater/` |

Read only the selected module and the resources it requires. Inside that module, resolve `<SKILL_DIRECTORY>`, relative scripts, references, schemas, templates and scaffolds from its **own resource base**, not this parent directory and not the target project. Each module's resource layout is intact. Its original `SKILL.md` is named `WORKFLOW.md` here so Codex does not discover nested duplicate skills; references to "this SKILL.md" mean that module entrypoint and its containing folder. Use its own validator; do not substitute the other module's similarly named script.

The selected target above supplies the module's project root even where its older prose says "active workspace." Preserve all other module logic and acceptance criteria.

### Build

Follow the builder's complete one-shot adoption/restructuring workflow. Use its existing `create_build_record.py`, classification and preservation ledger, ordered operations, managed instruction blocks, source-backed documentation, and full validator. The builder already determines the appropriate adopt/restructure/audit operation from the actual request. Do not substitute scaffolding alone for a completed build.

### Update

Follow the updater's existing preflight before initializing an update record or changing documents. The project must already have the compatible documentation system established by a prior build/one-shot adoption.

A claimed earlier run or an arbitrary docs folder is not proof of compatibility: use `references/updater/scripts/prepare_update.py preflight --project-root <PROJECT_ROOT>`. Exit 2 remains a stop, not permission to adopt, migrate or restructure. Explain the missing/incompatible structure and recommend `$ai-documentation-manager build` for that target. Do not automatically run build. Successful preflight still requires the updater's source routing, complete change classification, scoped update and task-scoped validator.

Use the current task's requested changes and source evidence as the updater specifies. If the scope is unclear, ask for the missing change context rather than documenting unrelated work.

The original initializer's draft ledger has a known operation-label mismatch with its validator. See [Preserved Updater Limitation](README.md#preserved-updater-limitation) when completing the ledger; keep the existing validator contract and truthful evidence, without broadening the update.

## Original names and generated instructions

The nested packages retain their original names, entrypoint contents, helper messages and templates byte-for-byte. Only the two entrypoint filenames change to `WORKFLOW.md`. Within this combined workflow, translate their invocation references as follows:

| Original reference | Combined invocation |
|---|---|
| `$project-documentation-builder` | `$ai-documentation-manager build` |
| `$project-documentation-updater` | `$ai-documentation-manager update` |

Apply this naming translation in user-facing guidance and managed instruction text generated for the target project. Do not edit bundled scripts/templates to rename their internals, rewrite raw audit evidence, or require the standalone skills to be installed. A recommendation to switch modes is not authorization to switch. Update generated `AGENTS.md` only where the selected module already permits it; preserve all project-owned content outside managed blocks.

## Completion

Use the selected module's completion contract: report the target, documented changes or unchanged classification, index status, exact ledger/audit paths, actual validator result and remaining blockers. Keep its existing output roots under `documents/documentation/` and `documents/tasks/documentation/build/` or `update/`. Do not create an extra parent workflow record or run the AI Development Workflow.

This wrapper grants no application-source changes, commits, pushes, deployments, external messages or destructive cleanup beyond the selected module's existing scope. Report only verification actually performed.
