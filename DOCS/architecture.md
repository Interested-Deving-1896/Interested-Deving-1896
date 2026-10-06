# Architecture

Interested-Deving-1896 maintains a personal profile, two independent
organization identities, and a public documentation site from one repository.
The organization READMEs are templates, not copies of the personal profile.

```text
README.md                              personal profile

profiles/osp/README.md
  ├─► OpenOS-Project-OSP/OpenOS-Project-OSP:README.md
  └─► OpenOS-Project-OSP/.github:profile/README.md

profiles/ooc/README.md
  ├─► OpenOS-Project-Ecosystem-OOC/OpenOS-Project-Ecosystem-OOC:README.md
  └─► OpenOS-Project-Ecosystem-OOC/.github:profile/README.md

DOCS/
  ├─► GitBook through .gitbook.yaml
  └─► GitHub Pages through mdBook and GitHub Actions
```

## Identity boundary

The publication manifest requires the appropriate organization identity in
each template and rejects personal-profile names. Publishing only updates the
four declared README files. It never mirrors the complete repository or copies
the personal README into an organization.

## Documentation boundary

GitBook and mdBook consume the same `DOCS/` source and `DOCS/SUMMARY.md`
navigation. Generated reference pages come from checked-in configuration and
are validated before either documentation system builds.
