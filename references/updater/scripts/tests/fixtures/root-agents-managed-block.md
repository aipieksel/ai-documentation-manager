<!-- BEGIN MANAGED BLOCK: agent-documentation-system -->
## Start Here

1. Agents MUST read [`documents/documentation/0-index.md`](documents/documentation/0-index.md).
2. Agents MUST read [`documents/documentation/project-overview.md`](documents/documentation/project-overview.md) when product, stack, source-tree, lifecycle, or runtime context is required.
3. Agents MUST extract exact wording and keywords from the user request and the initial plan.
4. Agents MUST search the root index for every feature term, UI label, command, data path, source path, lifecycle state, and error string.
5. Agents MUST read every matched primary and supporting document before editing implementation.
6. Agents MUST inspect the authoritative source paths listed by the index.
7. Agents MUST include routed automated and manual verification in the plan.

## Documentation Planning Contract

- `documents/documentation/0-index.md` is the only documentation routing index.
- Current implementation documentation MUST live under `documents/documentation/application/`.
- `documents/documentation/project-overview.md` MUST remain high-level.
- Folder-level index files MUST NOT be created.
- Separate search-index JSON, keyword-only indexes, source-context maps, documentation workflow pages, documentation templates, and generator audit folders MUST NOT be created under `documents/documentation/`.
- Existing canonical documents MUST be updated instead of creating competing contracts.
- Operational records and generated evidence MUST remain separate from current application contracts.
- Unverified findings MUST be recorded under `documents/documentation/agent-observations/`.
- Every move, rename, addition, removal, or reorganization MUST update `documents/documentation/0-index.md` in the same run.
- Documentation reorganization MUST preserve substance and MUST pass the validator bundled with the invoked one-shot documentation skill before completion.

## Planning Completion Contract

A complete plan MUST identify the behavior being changed, owning source modules and data paths, affected cross-cutting boundaries, required automated and manual verification, documentation updates required after verification, and unresolved risks that belong in observation records. Generated output, old plans, screenshots, reports, and backups MUST NOT override current source authority.

## Maintenance Entry Point

After implementation, configuration, workflow, verification, or documentation-routing changes, agents MUST update the routed canonical documents and synchronize `documents/documentation/0-index.md`. Use `$project-documentation-builder` for future full adoption or restructuring when that skill is available.
<!-- END MANAGED BLOCK: agent-documentation-system -->
