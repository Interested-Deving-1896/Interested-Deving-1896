# Contributing to Interested-Deving-1896

Thank you for helping improve this profile, its documentation, and the
organization-profile templates it publishes.

## Choose the right place

- Use this repository for the Interested-Deving-1896 profile, profile
  documentation, and the canonical OSP/OOC profile templates.
- For changes to a specific software project, use that project's source
  repository rather than its mirror.
- For security concerns, follow [SECURITY.md](SECURITY.md) and do not open a
  public issue containing sensitive details.
- For general help, see [SUPPORT.md](SUPPORT.md).

## Before opening a change

1. Search existing issues and pull requests for related work.
2. Keep the change focused on one outcome.
3. Preserve the identity boundary between Interested-Deving-1896, OSP, and
   OOC. Organization templates must contain only their own public identity.
4. Keep operational documentation factual. Clearly label fictional creative
   material and keep it under `characters/lore/`.
5. Use descriptive link text, meaningful headings, and accessible language.

Run the available local checks before submitting:

```bash
python3 scripts/profile_readmes.py validate
python3 scripts/profile_readmes.py generate-docs --check
python3 scripts/readme_policy.py --readme README.md --policy config/readme-policy.json quality
```

If your change affects generated content, update its canonical source and
regenerate the output instead of editing generated files by hand.

## Pull requests

Explain what changed, why it belongs here, how it was checked, and any
accessibility or mirror-chain impact. Maintainers may ask for revisions or move
the proposal to a more appropriate source repository.

## Licensing status

This repository does not currently declare a project license. Do not add or
assume one without an explicit maintainer decision. By contributing, you
confirm that you have the right to submit the material; submission alone does
not create a license for reuse.

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
