# Publication authentication and repository settings

The organization-profile publisher is ready to use a narrowly scoped GitHub
App. Until the App is installed, validated source changes remain safe: the
publisher validates them and skips cross-repository writes when no credential
is available.

## Preferred GitHub App configuration

Create one private GitHub App and install it separately in
`OpenOS-Project-OSP` and `OpenOS-Project-Ecosystem-OOC`. Limit each installation
to that organization's named README repository and `.github` repository.

Grant these repository permissions:

- Contents: read and write
- Workflows: read and write
- Metadata: read

In `Interested-Deving-1896/Interested-Deving-1896`, configure:

- Actions variable `PROFILE_SYNC_APP_ID` with the App ID
- Actions secret `PROFILE_SYNC_PRIVATE_KEY` with a current App private key

The publication matrix requests a separate installation token for each
destination organization. OSP credentials are never passed to the OOC job, and
OOC credentials are never passed to the OSP job.

Fine-grained personal access tokens restricted to each organization's two
destination repositories can be used temporarily as
`PROFILE_SYNC_OSP_TOKEN` and `PROFILE_SYNC_OOC_TOKEN`. The broad legacy
`PROFILE_SYNC_TOKEN` is retained only for migration and should be removed after
the App is verified.

Run **Publish organization READMEs** manually with `dry_run` enabled after
installing the App. A successful dry run should report every destination as
current without creating a commit.

## Social preview images

The prepared 1280×640 preview assets are:

- `assets/social-preview.png`
- `profiles/osp/assets/social-preview.png`
- `profiles/ooc/assets/social-preview.png`

GitHub does not provide a supported repository API for selecting a social
preview image. An administrator must upload the matching PNG in each
repository's **Settings → General → Social preview** panel. The SVG files beside
the PNGs are the editable canonical artwork.

## Owner decisions still required

A repository license must be selected explicitly before adding `LICENSE`.
Likewise, `CODEOWNERS` should be added only after confirming assignable users or
organization team slugs for all three repositories.
