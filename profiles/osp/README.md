# OpenOS-Project-OSP

<!-- README-AUTO:start:badges -->
[![GitHub namespace](https://img.shields.io/badge/GitHub-OpenOS--Project--OSP-181717?logo=github&style=flat-square)](https://github.com/OpenOS-Project-OSP)
[![GitLab mirror](https://img.shields.io/badge/GitLab-openos--project-fc6d26?logo=gitlab&logoColor=white&style=flat-square)](https://gitlab.com/openos-project)
[![README quality](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP/actions/workflows/readme-quality.yml/badge.svg)](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP/actions/workflows/readme-quality.yml)
<!-- README-AUTO:end:badges -->

**Operational continuity for open systems.**

**Preserve · Verify · Recover.**

OpenOS-Project-OSP is the operational continuity namespace of the OpenOS
Project. It keeps inspectable, independently verifiable copies of open-source
systems work across multiple Git forges, including its current GitHub and
GitLab endpoints.

[GitHub namespace](https://github.com/orgs/OpenOS-Project-OSP/repositories) ·
[GitLab namespace](https://gitlab.com/openos-project) ·
[OpenOS Project links](https://linktr.ee/OpenOS_Project)

## Role

This cross-forge namespace focuses on operational availability, provenance,
recovery, and reliable synchronization. Each hosted repository or project
remains responsible for its own status, license, upstream attribution, and
contribution instructions.

## Cross-forge terminology

OSP is platform-independent even though each hosting service supplies its own
account model and vocabulary:

- **Forge** means any Git hosting platform or independently hosted Git service.
- **Namespace** means OSP's top-level collaborative space: currently a GitHub
  organization and a GitLab group namespace.
- **Repository/project** means a hosted unit of source code and its associated
  collaboration features, regardless of the platform's preferred term.

Other forges may call the same concepts an account, group, team, workspace,
organization, repository, or project. Those labels do not change OSP's role or
the provenance and synchronization boundaries of the hosted content.

## Current focus

| Area | OSP responsibility |
|---|---|
| Operational continuity | Maintain accessible repository/project copies and recovery endpoints |
| Mirror integrity | Make synchronization direction, provenance, and drift visible |
| Open infrastructure | Support Linux, containers, filesystems, automation, and cross-forge workflows |
| Accessibility | Promote accessible documentation, WCAG checks, Braille, and text-to-speech tooling |
| Interoperability | Prefer open formats, portable workflows, and replaceable components |

## Mirror role

```text
OpenOS-Project-OSP/<repo>                 operational layer
             ├──────────► gitlab.com/openos-project/<subgroup>/<repo>
             │
             ▼
OpenOS-Project-Ecosystem-OOC/<repo>       ecosystem layer
```

Repositories or projects may be synchronized automatically. Before
contributing, consult the README and contribution guidance in the specific
hosted project.

## Working principles

- Preserve upstream attribution and licensing.
- Keep synchronization direction and hosted-project roles explicit.
- Treat accessibility, recovery, documentation, and operability as core work.
- Avoid dependence on a single forge, vendor, runtime, or deployment target.

## Creative identity

The OSP layer is represented by Relay's **Continuity Prism** expression and
Nexus's **Mirror Keeper** digital-cosplay costume. These are fictional creative
works and do not assert real-world affiliations, operations, or identities.

## Connect

- GitHub: [OpenOS-Project-OSP](https://github.com/OpenOS-Project-OSP)
- GitLab: [openos-project](https://gitlab.com/openos-project)
- Project links: [OpenOS_Project](https://linktr.ee/OpenOS_Project)
