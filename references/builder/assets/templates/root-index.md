# {{PROJECT_NAME}} — Documentation and Source Routing Index

> Status: {{STATUS}}  
> Last updated: {{LAST_UPDATED}}  
> Purpose: Single source of truth for task planning, documentation discovery, and source-context routing.

Search this file using the exact wording from the user request and the keywords from the initial plan. Follow every matching documentation and source route before changing implementation.

## Required Routing Procedure

1. Extract exact nouns, verbs, UI labels, feature names, commands, file paths, data paths, lifecycle states, and error text from the task.
2. Search this file case-insensitively for those terms and close aliases.
3. Read the primary document in every matching row and all supporting documents that cross the task boundary.
4. Inspect the listed source paths before planning edits.
5. Add the routed verification scope to the plan.
6. When no route matches, identify the owning source first and add the missing task wording to this index when documentation is updated.

## Authority Order

{{AUTHORITY_ORDER}}

## Status Legend

{{STATUS_LEGEND}}

## Documentation Map

| Need | Read |
| --- | --- |
{{DOCUMENTATION_MAP_ROWS}}

## Keyword and Source Routing Matrix

| Search terms from the task or plan | Primary documentation | Source context to inspect | Also read when relevant |
| --- | --- | --- | --- |
{{ROUTING_ROWS}}

## Source-Path Router

| Source path or area | Ownership / purpose | Documentation route |
| --- | --- | --- |
{{SOURCE_PATH_ROWS}}

## Cross-Cutting Planning Packs

| Change type | Minimum documentation set | Additional source and verification scope |
| --- | --- | --- |
{{PLANNING_PACK_ROWS}}

## Application Documentation Inventory

| File | Scope | Status |
| --- | --- | --- |
{{APPLICATION_INVENTORY_ROWS}}

## Operational and Historical Records

{{OPERATIONAL_RECORDS}}

## Documentation Maintenance Rules

1. Keep this file as the only root routing and source-context index.
2. Do not create folder-level indexes, a second root index, a keyword-only file, a JSON search index, a separate source-context map, a documentation workflow page, or documentation templates.
3. Put current implementation detail in the owning document under `application/`; keep `project-overview.md` high-level.
4. Update this index whenever a document or source path is moved, renamed, added, removed, or reorganized.
5. Add real task wording when an agent could not route a request using existing terms.
6. Prefer updating an existing contract over creating a duplicate document.
7. Keep operational records and generated evidence separate from source authority.
8. Record unverified findings in `agent-observations/`.
9. Verify every current-document relative link and source path after documentation changes.

## Completion Check for Task Plans

Before implementation, a plan MUST identify:

- the task keywords used for routing;
- every primary and supporting document read;
- the authoritative source modules, data paths, interfaces, scripts, and configuration involved;
- cross-cutting persistence, lifecycle, responsive, integration, deployment, and compatibility effects where applicable;
- targeted automated tests and required manual/browser verification;
- documentation updates required after behavior is verified;
- unresolved risks that belong in observation records.
