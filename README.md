<!-- AI:skip -->

# Interested Deving

**Deving for the future.**

Open-source systems engineering across Linux, automation, containers,
accessibility, AI-assisted tooling, and reproducible infrastructure.

[Source workspace](https://github.com/Interested-Deving-1896) ·
[OSP mirror](https://github.com/OpenOS-Project-OSP) ·
[OOC ecosystem](https://github.com/OpenOS-Project-Ecosystem-OOC) ·
[GitLab mirrors](https://gitlab.com/openos-project)

## Open engineering workspace

`Interested-Deving-1896` is the source workspace for the OpenOS Project
ecosystem. It brings together original projects, integration layers,
infrastructure automation, and curated upstream mirrors with a common goal:
make open systems easier to build, operate, recover, and adapt across platforms.

Work is source-first here. Downstream GitHub and GitLab copies provide
continuity, wider access, and independently verifiable mirrors.

## Current focus

| Area | What is being built |
|---|---|
| Linux lifecycle | Image building, live systems, recovery, immutable-system patterns, OTA updates, kernels, and filesystems |
| Platform-agnostic automation | Common HTTP and CLI interfaces across filesystems, Git platforms, browsers, operating systems, and AI backends |
| Containers and virtual machines | Incus/LXC tooling, image infrastructure, deployment helpers, and cross-platform workflows |
| Developer infrastructure | Repository orchestration, CI recovery, observability, documentation, and multi-forge synchronization |
| Accessibility | Assistive technology, accessible documentation, WCAG auditing, Braille, and text-to-speech tooling |
| AI-assisted engineering | Practical agents for diagnostics, guided builds, repository maintenance, and project knowledge |

## Start here

| Project | Purpose |
|---|---|
| [`fork-sync-all`](https://github.com/Interested-Deving-1896/fork-sync-all) | Control plane for repository mirroring, upstream sync, maintenance workflows, documentation, and cross-forge operations |
| [`unified-agnostic-api`](https://github.com/Interested-Deving-1896/unified-agnostic-api) | Shell-first HTTP and CLI layer for filesystem, GitHub, browser, OS, and AI backends |
| [`eggs-ai`](https://github.com/Interested-Deving-1896/eggs-ai) | AI agent for Penguins Eggs diagnostics, guided ISO building, configuration, and knowledge-base Q&A |
| [`penguins-eggs-integrations`](https://github.com/Interested-Deving-1896/penguins-eggs-integrations) | Integration plugins connecting Penguins Eggs with projects across the wider ecosystem |
| [`infra-dashboard`](https://github.com/Interested-Deving-1896/infra-dashboard) | Operational dashboards and supporting services for infrastructure visibility |

Explore the [repositories](https://github.com/Interested-Deving-1896?tab=repositories)
for the full workspace. Source repositories and tracked upstream projects evolve
quickly, so each repository README remains the authority for its own status and
usage.

## Fork-Sync-All mirror chain 🪞

[`fork-sync-all`](https://github.com/Interested-Deving-1896/fork-sync-all)
maintains the outward mirror chain and verifies drift between its GitHub and
GitLab destinations.

```text
Interested-Deving-1896/<repo>                  source
              │
              ▼
OpenOS-Project-OSP/<repo>                      operational mirror
              ├──────────► gitlab.com/openos-project/<subgroup>/<repo>
              │
              ▼
OpenOS-Project-Ecosystem-OOC/<repo>            ecosystem mirror
              └──────────► gitlab.com/openos-project-ooc-ecosystem/<subgroup>/<repo>
```

Open issues and pull requests against the source repository unless a mirror
explicitly says otherwise. Mirror copies are continuity endpoints and may be
force-synchronized from their upstream source.

## Working principles

- Prefer open formats, inspectable automation, and reproducible workflows.
- Design for more than one distribution, runtime, forge, or deployment target.
- Treat accessibility, recovery, documentation, and operability as core features.
- Preserve upstream attribution and make the direction of synchronization clear.

## Mascot and digital cosplay 📖

The Mirrorchain has two fictional creative representatives:

- **Relay** *(working title)* is an independent ecosystem mascot embodying
  openness, resilience, accessibility, and continuity across the source, OSP,
  and OOC layers.
- **Nexus, the Mirrorchain Weaver** *(working title)* is the digital cosplay
  persona used by Interested-Deving-1896 for character studies and
  open-source worldbuilding.

[Meet the characters](characters/README.md) ·
[View the reference artwork](characters/assets/README.md) ·
[Explore the Mirrorchain lore](characters/lore/MIRRORCHAIN.md) ·
[Read the creative provenance](characters/PROVENANCE.md)

> These characters and stories are fictional creative works. They are separate
> from technical documentation and do not assert real-world affiliations,
> operations, or identities.

## Connect

- GitHub: [@Interested-Deving-1896](https://github.com/Interested-Deving-1896)
- OpenOS Project links: [linktr.ee/OpenOS_Project](https://linktr.ee/OpenOS_Project)
- Contributions: use the issue tracker or pull requests in the relevant source repository

---

[![Built with Ona](https://ona.com/build-with-ona.svg)](https://app.ona.com/#https://github.com/Interested-Deving-1896/Interested-Deving-1896)
