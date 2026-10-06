# Organization README publication

Organization README content is maintained in two canonical templates:

- [`profiles/osp/README.md`](../profiles/osp/README.md)
- [`profiles/ooc/README.md`](../profiles/ooc/README.md)

The destination allowlist is stored in
[`config/profile-targets.json`](../config/profile-targets.json). Changes to a
template and repository-specific policy are validated. The template can then be
published to its organization-named repository and special
`.github/profile/README.md` destination; the policy is published only to the
organization-named repository.

The same manifest separately allowlists portable repository automation. Those
files are mirrored unchanged to the two organization-named README repositories
and derive their active identity from `github.repository_owner`; organization
profile repositories continue to receive only `profile/README.md`.

## Workflows

| Workflow | Responsibility |
|---|---|
| `Validate profile READMEs` | Validate Markdown structure, local links, identities, and generated documentation |
| `Publish organization READMEs` | Update allowlisted profile, policy, and shared automation files |
| `Verify organization README drift` | Compare all remote files byte-for-byte with their canonical templates |
| `Build and deploy documentation` | Build the shared `DOCS/` source and deploy it to GitHub Pages |
| `README quality gate` | Enforce each repository's identity, managed blocks, links, structure, and accessibility-oriented checks |
| `README rendered preview` | Produce responsive HTML, desktop/mobile screenshots, plain text, and optional audio/Braille artifacts |
| `README maintenance proposals` | Report staleness or propose reconciliation, translation, and AI-assisted edits through reviewable pull requests |

## Shared repository automation

The organization-named README repositories receive these portable workflows:

- guarded, collaborator-invoked AI assistance;
- read-only repository and workflow auditing;
- manual sanitized support-bundle generation;
- a local content server/client smoke test;
- a contributor-association trust gate for automation-sensitive changes; and
- path-based pull-request labeling;
- policy-driven README quality reports;
- rendered and accessible preview artifacts; and
- manual, pull-request-only maintenance proposals.

The workflow engines under `scripts/` are mirrored unchanged. Each named README
repository instead receives its own `config/readme-policy.json`, so OSP and OOC
retain their own required identity, headings, badges, and managed content.

Fork-Sync-All control-plane jobs that mutate other repositories, operate the
FSA API, deliver diagnostics externally, or require the full cross-forge vouch
registry are intentionally excluded.

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

AI-assisted translation and drafting are opt-in. Configure the repository
variable `README_AI_ENDPOINT` with an HTTPS OpenAI-compatible chat-completions
endpoint and the secret `README_AI_TOKEN`; `README_AI_MODEL` may override the
model declared in the local policy. Generated content is an artifact and, when
requested, a pull request—never a direct update to the default branch.

Opening a proposal pull request uses `README_MAINTENANCE_TOKEN` when present.
Use a narrowly scoped fine-grained token with Contents and Pull requests
read/write access to that repository. Without it, the workflow uses the built-in
token only when the repository permits Actions to create pull requests;
otherwise it retains the proposal as a downloadable artifact. This keeps the
broader repository-wide “create and approve pull requests” permission optional.

## Local commands

```bash
python3 scripts/profile_readmes.py validate
python3 scripts/profile_readmes.py generate-docs --check
python3 scripts/readme_policy.py quality --report readme-report.json
python3 scripts/readme_policy.py staleness
PROFILE_SYNC_TOKEN=... python3 scripts/profile_readmes.py sync --check
PROFILE_SYNC_TOKEN=... python3 scripts/profile_readmes.py sync --dry-run
```
