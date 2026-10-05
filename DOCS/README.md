# Interested-Deving-1896 documentation

This page is the documentation map for the Interested-Deving-1896 profile and
its place in the OpenOS Project mirror chain. It brings the public-facing parts
of the automation documentation together without duplicating project-specific
secrets, quota tables, generated artifacts, or runbooks that must remain
versioned with the automation source.

## Profile and architecture

| Resource | Purpose |
|---|---|
| [Profile README](../README.md) | Workspace overview, current focus, principles, and entry points |
| [Automation documentation](https://interested-deving-1896.github.io/fork-sync-all/) | Published reference for the mirror and maintenance control plane |
| [Architecture](https://interested-deving-1896.github.io/fork-sync-all/architecture.html) | Three-organization chain, GitLab leg, and data flow |
| [Workflow reference](https://interested-deving-1896.github.io/fork-sync-all/workflow-triggers.html) | Workflow groups, triggers, schedules, and dependencies |
| [Organization README repositories](#repository-roles) | Standalone OSP and OOC README repositories and special organization profiles |
| [Accessibility reference](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/accessibility.md) | Accessible README checks, WCAG auditing, audio, and Braille output |
| [Operational runbooks](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/runbooks.md) | Recovery and incident-response procedures |

## Complete automation reference

The canonical documentation index remains
[`DOCS/SUMMARY.md`](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/SUMMARY.md).
These direct links cover its main hand-written references:

| Resource | Purpose |
|---|---|
| [GitHub Actions limits and operations](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/OPERATIONS.md) | Platform limits, concurrency, and operational constraints |
| [Workflow scheduling](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/workflow-scheduling.md) | Dispatch windows, timing, and quota-aware scheduling |
| [Quota costs](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/quota-costs.md) | Per-workflow API cost estimates and budgeting |
| [AI agent costs](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/ai-agent-costs.md) | Agent cost profiles, tokenizers, and task estimates |
| [AI-agnostic skills API](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/agent-skills-api.md) | Portable skill discovery, validation, and export |
| [OTA system](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/ota-system.md) | Versioned delivery architecture and opt-in guidance |
| [OTA reconciliation](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/ota-reconcile.md) | Drift detection and recovery paths |
| [Pre-flush checklist](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/pre-flush-checklist.md) | Pre-flight checks for a full mirror-chain run |
| [Support bundles](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/support-bundles.md) | Diagnostic collection and support artifacts |
| [Contributing to the automation](https://github.com/Interested-Deving-1896/fork-sync-all/blob/main/DOCS/contributing.md) | Workflow, script, configuration, and test guidance |

Generated references—including the source tree, glossary, registered imports,
subgroup map, workflow reference, origins, and eco audit—are linked from the
canonical index so their URLs and generated counts stay synchronized with the
control-plane repository.

## Repository roles

| Repository | Role |
|---|---|
| [`Interested-Deving-1896/Interested-Deving-1896`](https://github.com/Interested-Deving-1896/Interested-Deving-1896) | Canonical profile and source README |
| [`OpenOS-Project-OSP/OpenOS-Project-OSP`](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP) | Standalone OSP README repository; suitable for pinning on the OSP organization page |
| [`OpenOS-Project-Ecosystem-OOC/OpenOS-Project-Ecosystem-OOC`](https://github.com/OpenOS-Project-Ecosystem-OOC/OpenOS-Project-Ecosystem-OOC) | Standalone OOC README repository; suitable for pinning on the OOC organization page |
| [`OpenOS-Project-OSP/.github`](https://github.com/OpenOS-Project-OSP/.github) | OSP organization-profile README source |
| [`OpenOS-Project-Ecosystem-OOC/.github`](https://github.com/OpenOS-Project-Ecosystem-OOC/.github) | OOC organization-profile README source |

## Creative documentation

| Resource | Purpose |
|---|---|
| [Character index](../characters/README.md) | Relay and Nexus roles, layer variants, and boundaries |
| [Mirrorchain folklore](../characters/lore/MIRRORCHAIN.md) | Fictional translation of source, continuity, and ecosystem layers |
| [Creative provenance](../characters/PROVENANCE.md) | Ideation history, KDE influence, digital sovereignty, and AI disclosure |
| [Creative-work license](../characters/LICENSE.md) | CC BY-SA 4.0 terms for original work under `characters/` |

## Contribution direction

Open issues and pull requests against the relevant repository in the
`Interested-Deving-1896` source organization. OSP, OOC, and GitLab copies are
continuity endpoints unless a repository explicitly states otherwise. Preserve
upstream attribution and keep synchronization direction visible in all derived
documentation.
