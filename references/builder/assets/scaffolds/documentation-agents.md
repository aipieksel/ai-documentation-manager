# Documentation Agent Contract

This file is the mandatory documentation-folder entry point for implementation planning and documentation maintenance. It exists so project agents can change documentation routing behavior without requiring every planning skill to duplicate project-specific rules.

## Start Here

1. Read [`0-index.md`](0-index.md) immediately after this file.
2. Read [`project-overview.md`](project-overview.md) when product, stack, source-tree, lifecycle, runtime, architecture, or operational context is required.
3. Extract exact wording and keywords from the user request and the initial plan.
4. Search `0-index.md` for every feature term, UI label, command, route, file path, lifecycle state, error string, data path, source path, and contract term.
5. Read every matched primary and supporting document before inspecting or editing implementation.
6. Inspect the authoritative source paths listed by the index. Current source, configuration, schemas, tests, and runtime manifests are authoritative.
7. Include routed automated, browser/manual, operational, and documentation verification in the plan whenever the task affects those surfaces.

## Documentation-First Planning Gate

Before non-trivial implementation or documentation-structure work, read this file, route the task through `0-index.md`, inspect every matched document and authoritative source path, and include the required verification and documentation closeout in the active plan or checklist. Follow any project task workflow that already applies, but do not require a separate planning package merely to use this documentation system.

## Documentation Contract

- [`0-index.md`](0-index.md) is the only documentation routing and source-context index.
- Current implementation contracts live under `application/`.
- Task workflow, active plans, lessons, verification policy, evidence, and daily task logs live outside `documents/documentation/` under the configured task root.
- Historical implementation records, generated QA evidence, design artifacts, old documentation roots, and task plans are operational evidence only; do not treat them as current source authority.
- Update an existing application document rather than creating a competing contract for the same feature or source surface.
- Keep [`project-overview.md`](project-overview.md) high-level.
- Add missing real-world task wording to the existing routing matrix in `0-index.md` when routing fails.
- Do not recreate separate root keyword lists, JSON search indexes, source-context maps, documentation workflow files, folder-level indexes, generator audit folders, or documentation templates under `documents/documentation/`.
- Record unresolved anomalies, blockers, and recommendations in the matching file under [`agent-observations/`](agent-observations/).

## Authority Order

1. Current implementation source, configuration, schemas, scripts, tests, and runtime manifests.
2. Current application documentation under `application/`.
3. [`0-index.md`](0-index.md) and [`project-overview.md`](project-overview.md).
4. Package/build/runtime manifests and operational configuration.
5. Operational records under the configured task root and documentation reports.
6. Historical records and archived plans.

## Verification Contract

Use the verification surfaces named by the matched documentation and task plan. Confirm source-level correctness, runtime behavior, data-contract boundaries, responsive/browser-visible behavior, and documentation-routing integrity whenever the task affects those surfaces. Do not mark documentation or implementation complete until the routed verification evidence is recorded or the remaining gap is explicitly documented as a blocker/waiver.

## Completion Check

Before claiming planning or documentation routing is complete, confirm this file was read first, the routed index was searched with the task's exact wording, every matched document was read, and the relevant source paths were inspected or explicitly deferred with a recorded blocker.
