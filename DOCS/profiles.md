# Organization README publication

Organization README content is maintained in two canonical templates:

- [`profiles/osp/README.md`](../profiles/osp/README.md)
- [`profiles/ooc/README.md`](../profiles/ooc/README.md)

The destination allowlist is stored in
[`config/profile-targets.json`](../config/profile-targets.json). Changes to a
template are validated and can then be published to its organization-named
repository and special `.github/profile/README.md` destination.

## Workflows

| Workflow | Responsibility |
|---|---|
| `Validate profile READMEs` | Validate Markdown structure, local links, identities, and generated documentation |
| `Publish organization READMEs` | Update only the four allowlisted destination files |
| `Verify organization README drift` | Compare all remote files byte-for-byte with their canonical templates |
| `Build and deploy documentation` | Build the shared `DOCS/` source and deploy it to GitHub Pages |

## Credential boundary

Cross-repository publication requires `PROFILE_SYNC_TOKEN`, preferably a
fine-grained personal access token or GitHub App installation token with
Contents read/write access to only these repositories:

- `OpenOS-Project-OSP/OpenOS-Project-OSP`
- `OpenOS-Project-OSP/.github`
- `OpenOS-Project-Ecosystem-OOC/OpenOS-Project-Ecosystem-OOC`
- `OpenOS-Project-Ecosystem-OOC/.github`

The broad Fork-Sync-All synchronization token is deliberately not used.
Without `PROFILE_SYNC_TOKEN`, publication safely skips while validation and
public drift checks remain available.

## Local commands

```bash
python3 scripts/profile_readmes.py validate
python3 scripts/profile_readmes.py generate-docs --check
PROFILE_SYNC_TOKEN=... python3 scripts/profile_readmes.py sync --check
PROFILE_SYNC_TOKEN=... python3 scripts/profile_readmes.py sync --dry-run
```
