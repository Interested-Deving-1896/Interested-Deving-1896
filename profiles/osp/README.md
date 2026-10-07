# OpenOS-Project-OSP

<!-- README-AUTO:start:badges -->
[![GitHub namespace](https://img.shields.io/badge/GitHub-OpenOS--Project--OSP-181717?logo=github&style=flat-square)](https://github.com/OpenOS-Project-OSP)
[![GitLab mirror](https://img.shields.io/badge/GitLab-openos--project-fc6d26?logo=gitlab&logoColor=white&style=flat-square)](https://gitlab.com/openos-project)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-00aacc?style=flat-square)](https://openos-project-osp.github.io/OpenOS-Project-OSP/)
[![README quality](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP/actions/workflows/readme-quality.yml/badge.svg)](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP/actions/workflows/readme-quality.yml)
[![OpenCollective tiers](https://img.shields.io/badge/OpenCollective-support%20tiers-7FADF2?logo=opencollective&logoColor=white&style=flat-square)](https://opencollective.com/openos-project/contribute)
<!-- README-AUTO:end:badges -->

**Operational continuity for open systems.**

**Preserve · Verify · Recover.**

OpenOS-Project-OSP is the operational continuity namespace of the OpenOS
Project. It keeps inspectable, independently verifiable copies of open-source
systems work across multiple Git forges, including its current GitHub and
GitLab endpoints.

[GitHub namespace](https://github.com/orgs/OpenOS-Project-OSP/repositories) ·
[GitLab namespace](https://gitlab.com/openos-project) ·
[Documentation](https://openos-project-osp.github.io/OpenOS-Project-OSP/) ·
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

## Forge-neutral README subsystem

OpenOS-Project-OSP consumes reusable policy and rendered-link engines from
Fork-Sync-All through its profile publication pipeline. Its own README content
remains OpenOS-Project-OSP-specific. The shared contract calls this hosting
boundary a **namespace** and this repository a **project**, allowing an
equivalent GitLab group/subgroup or another forge layout to participate without
renaming it an organization.

Subsystem files are generated consumers here; reusable changes are contributed
to Fork-Sync-All and identity changes to the OpenOS-Project-OSP profile source,
then published forward.

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

## OpenCollective support-tier template

<!-- SUPPORT-TIERS:START -->
The [OpenOS Project OpenCollective](https://opencollective.com/openos-project) connects transparent
contributions to named public purposes. Its
[current contribution options](https://opencollective.com/openos-project/contribute) remain
the source of truth for live offerings.

This operational-continuity view maps contribution purposes to OSP responsibilities.
A tier is a contribution purpose—not a rank, entitlement, governance role,
security clearance, or access level.

### Contribution-purpose summary

| Tier family | Supported public work |
|---|---|
| Continuity infrastructure | Mirrors, hosting, storage, recovery, deployment, and self-hosted services |
| Engineering operations | Automation, releases, supporting technologies, and maintenance |
| Contributor operations | User support, development hardware, and contracted work |
| Resilient infrastructure | Environmental and long-term operational proposals |
| Shared logistics | Distribution, shipping, and cross-namespace operational costs |

The live OpenCollective listing is authoritative for availability, wording, amounts, fulfillment, and financial terms.
A contribution expresses support for the stated purpose; it does not
purchase governance authority or guarantee delivery of a proposal, service,
or benefit.

This factual operational block is generated from the canonical structured
support-tier configuration.
Fictional tier narratives remain exclusively under `characters/lore/`.
<!-- SUPPORT-TIERS:END -->

## Creative identity

The OSP layer is represented by Relay's **Continuity Prism** expression and
Nexus's **Mirror Keeper** digital-cosplay costume. These are fictional creative
works and do not assert real-world affiliations, operations, or identities.

[Read the fictional OSP Continuity Ledger](https://github.com/OpenOS-Project-OSP/OpenOS-Project-OSP/blob/main/characters/lore/STEWARDSHIP-LEDGER.md).

## Connect

- GitHub: [OpenOS-Project-OSP](https://github.com/OpenOS-Project-OSP)
- GitLab: [openos-project](https://gitlab.com/openos-project)
- Project links: [OpenOS_Project](https://linktr.ee/OpenOS_Project)
- Repository guidance: [Contributing](CONTRIBUTING.md) · [Support](SUPPORT.md) · [Security](SECURITY.md) · [Accessibility](ACCESSIBILITY.md)
