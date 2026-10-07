# Forge-neutral README subsystem

OpenOS-Project-Ecosystem-OOC uses a reusable README subsystem without treating
a GitHub organization as the universal model for every forge.

- **Namespace** means the containing account, organization, group, subgroup,
  workspace, or equivalent boundary.
- **Project** means this hosted Git repository.
- **Profile surface** means the README location exposed by the current forge.

Fork-Sync-All owns reusable policy and rendered-link engines.
OpenOS-Project-Ecosystem-OOC owns this project's identity, purpose, links, and
contribution guidance. Generated files flow into this project in one direction,
preventing a circular mirror from overwriting ecosystem-specific content.

Reusable changes should be promoted to their engine owner. OOC-specific content
changes should be made in the OpenOS-Project-Ecosystem-OOC profile source and
then published through the normal pipeline.
