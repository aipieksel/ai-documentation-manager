# Project Documentation Updater

Maintains an existing canonical documentation system under `documents/documentation/`. Every run records its routing decisions and validation evidence in a unique folder under `documents/tasks/documentation/update/`.

Invoke with `$project-documentation-updater`. It is self-contained and intentionally refuses to bootstrap an incompatible project; use `$project-documentation-builder` for initial adoption or structural repair.

For visible-UI claims, follow the target project's browser policy. Ego Browser is recommended when installed and authorized, but it is not a dependency for non-browser documentation work.
