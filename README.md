# AI Documentation Manager

Maintained by [aipieksel](https://github.com/aipieksel). Upstream credits and licenses remain with their respective authors.

AI Documentation Manager is a Codex skill for creating and maintaining project documentation that stays tied to current source. It gives a project one routing index, a high-level overview, focused application documents, and an evidence trail for changes. The goal is to make a codebase understandable without letting old plans or generated artifacts masquerade as current behavior.

Use `build` when adopting the system or restructuring existing docs, and `update` for a bounded change after a compatible system is established. The skill checks the target project, preserves existing substance, routes work to the right documents, and runs the bundled validator. It changes documentation; it does not change the application itself.

| Mode | Purpose | Existing system required? |
| --- | --- | --- |
| `build` | One-shot documentation adoption or comprehensive restructuring | No |
| `update` | Focused maintenance after source, configuration, workflow or behavior changes | Yes, confirmed by preflight |

## Quick Start

In the Codex composer, type `/aidm`, select **AI Documentation Manager**, press Tab, then append the mode. For example:

```text
/aidm + Tab, then build
/aidm + Tab, then update
```

The shorthand selects the skill; it is not a separately registered command. Client autocomplete behavior can vary. The canonical invocation works independently of that shorthand:

```text
$ai-documentation-manager build
$ai-documentation-manager update
```

`Build` and `Update` also work. A bare skill mention asks which mode you need; it does not choose a potentially disruptive operation.

## Target Another Project

```text
$ai-documentation-manager build /path/to/project
$ai-documentation-manager build "~/Projects/My App"
$ai-documentation-manager update ./packages/my-app
```

Absolute, home-relative and relative paths are supported. Quote paths containing spaces. Relative paths resolve from the chat's working directory. An explicit folder takes precedence over the current workspace and previously discussed projects.

Without a folder, the skill establishes the current project root from the workspace and project instructions. It does not run against its own installation folder, guess between multiple projects or silently replace a subproject with a monorepo root.

For an update, include any change context that is not already available in the task. The updater routes the actual changed source and requested scope through the existing documentation index; it does not assume all dirty files belong to the task.

## Build

Build runs the existing documentation builder from start to finish:

- Inspect project instructions, documentation, source and verification evidence.
- Create the builder's unique operational record and preservation ledger.
- Classify existing documentation and establish final paths before moving files.
- Preserve substance, repair routes and write source-backed application contracts.
- Maintain the sole root index, project overview and managed `AGENTS.md` instructions.
- Run the original full structural validator and report its actual audit result.

Build supports initial adoption and comprehensive restructuring. It is not merely a folder generator. Unresolved classification, missing source evidence or a failing current-scope audit prevents a completion claim.

## Update

Update requires a compatible established system from a previous build or one-shot documentation run. The original preflight checks the actual structure and managed instructions; a historical claim that a build ran is not enough.

When preflight passes, the updater classifies the complete in-scope change, updates the smallest accurate document set, synchronizes affected routes, and runs its original task-scoped validator. Outcomes remain `required`, `not-required`, `audit-only` or `blocked`.

If the system is missing or incompatible, update stops and recommends `$ai-documentation-manager build`. It never performs a partial adoption or silently switches modes. An older one-shot system using a different root may require build/restructuring before this updater can maintain it.

## Project Outputs

The original modules retain their output layout:

```text
documents/
|-- documentation/
|   |-- 0-index.md
|   |-- project-overview.md
|   |-- AGENTS.md
|   |-- application/
|   `-- agent-observations/
`-- tasks/
    `-- documentation/
        |-- build/
        |   `-- YYYY-MM-DD-NNNNN-short-description/
        |       |-- ledger.json
        |       `-- audit.json
        `-- update/
            `-- YYYY-MM-DD-NNNNN-short-description/
                |-- ledger.json
                `-- audit.json
```

Root `AGENTS.md` remains the project entry point. Its managed documentation block is maintained without replacing project-owned instructions. The root README remains substantive, not a competing routing index. Operational records stay separate from current documentation.

## Package layout

The top-level [SKILL.md](SKILL.md) selects the mode. The original [builder](references/builder/WORKFLOW.md) and [updater](references/updater/WORKFLOW.md) retain their own references, helpers, and validators under `references/`. The [bundle manifest](references/bundle-manifest.json) checks that those resources remain intact, while `tests/` exercises the combined package.

Install the whole folder so relative references and validation tools remain available. The builder and updater are separate workflows behind one entry point; their validators are not interchangeable.

## Install

Requires an agent that supports local skills and Python 3.10 or newer. The workflow helpers and bundled regression tests use the Python standard library. No generator installation, MCP server, package manager or project-local skill copy is required.

Install or clone this **whole folder**, including both nested modules, into a Codex-discovered skill location such as `~/.agents/skills/ai-documentation-manager/`. Alternatively, keep the repository elsewhere and symlink its folder into that skill location. Do not install only the top-level `SKILL.md`.

Follow [Codex's skill discovery documentation](https://developers.openai.com/codex/skills/) for supported locations and client refresh behavior. If this folder already lives beneath one of your discovered skill roots, no additional link is needed.

## Validation

From this repository root:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s references/builder/scripts/tests -v
python3 -m unittest discover -s references/updater/scripts/tests -v
```

The bundle tests verify preserved file hashes and relocation, reject update on a fresh project without mutating it, and check that the relocated updater accepts a fixture established by the original builder test support. The original suites continue to test each module independently. All test project mutations are confined to temporary directories.

These are packaging and regression checks, not proof that an arbitrary project's documentation is accurate. Each real invocation must still complete its module's source review, preservation and validation gates.

### Updater ledger limitation

The updater's draft ledger labels currently differ from the labels accepted by its validator. When running an update, finish the ledger with the validator's operation names and record what actually happened; creating a draft alone does not pass validation. The [maintenance tests](references/updater/scripts/tests/test_maintenance_validation.py) show the accepted vocabulary.

## Scope

Build and update preserve the modules' original documentation-only authorization, protected paths, recovery requirements and verification standards. Neither mode authorizes application-code changes, commits, pushes, deployment or unrelated cleanup.

Browser verification is conditional on documented claims and project instructions, not a requirement for unrelated documentation work. No separate planning/checklist system is installed.

## Rights

The package is licensed under [MIT](LICENSE). Keep generated project records and private conversations outside the reusable skill folder.
