# Publishing

All three clients are published from this monorepo via a single `vX.Y.Z` git tag.
The `publish.yml` workflow runs the full test suite for each client whose directory
changed since the previous tag, then publishes it to its registry.

| Language | Package | Registry |
|---|---|---|
| Python | `kyccentral` | [PyPI](https://pypi.org/project/kyccentral/) |
| JavaScript | `@kyccentral/sdk` | [npm](https://www.npmjs.com/package/@kyccentral/sdk) |
| Elixir | `kyccentral` | [Hex](https://hex.pm/packages/kyccentral) |

## One-time setup

These are done once per repository (or once per account if you own all three
registries).

### PyPI (trusted publishing)

PyPI supports [trusted publishing](https://docs.pypi.org/trusted-publishers/) via OIDC,
so you do **not** need to create or store an API token. Instead, register this GitHub
repo as a trusted publisher:

1. Go to <https://pypi.org/manage/kyccentral/settings/publishing/> (you must own the
   `kyccentral` project on PyPI first).
2. Click **Add a new publisher**.
3. Select **GitHub** as the publisher.
4. Fill in:
   - Repository name: your GitHub repo (e.g. `qualia91/kyc-central-client`)
   - Workflow name: `publish.yml`
   - Environment name: (leave blank, or use `pypi` if you gate releases with an
     environment in GitHub)
5. Click **Add**.

After this, any `vX.Y.Z` tag pushed to `main` from this repo can publish to PyPI — no
secrets to rotate.

### npm (trusted publishing)

npm supports [trusted publishing](https://docs.npmjs.com/trusted-publishers/) via OIDC,
just like PyPI — no API token to store or rotate.

1. Ensure you own the `@kyccentral/sdk` package on npm under your account (publish
   once manually or claim it through the npm UI).
2. On <https://www.npmjs.com/>, go to your package settings for `@kyccentral/sdk`
   → **Trusted Publishing**.
3. Click **Add trusted publisher**.
4. Select **GitHub Actions** as the publisher and fill in:
   - Organization or user: your GitHub username (e.g. `qualia91`)
   - Repository: `kyc-central-client`
   - Workflow filename: `publish.yml`
   - Allowed actions: `npm publish` (and `npm stage publish` if you use snapshots)
5. Click **Add**.

Requirements: npm CLI 11.5.1+ (Node 22.14+; the publish workflow uses Node 24). The
workflow's `permissions: id-token: write` lets npm exchange the GitHub OIDC token for a
short-lived npm token automatically — no `NPM_TOKEN` secret is stored in GitHub.
`npm publish --provenance` is still used so every release is signed with an
[SLSA](https://slsa.dev/) attestation tied to this repo and tag (the `provenance: true`
flag in `package.json` also enables this).

### Hex (API key)

1. Log in to <https://hex.pm/> with your account.
2. Go to <https://hex.pm/dashboard> → **API Keys**.
3. Click **Create API Key**. Give it a descriptive name (e.g. `github-actions-publish`).
4. Select **Full access** (or at minimum `api key: publishes`).
5. Copy the key and save it as the **`HEX_API_KEY`** repository secret in GitHub:
   `Settings → Secrets and variables → Actions → New repository secret`.

## Per-release steps

Publishing happens automatically when a `vX.Y.Z` tag is pushed to the default branch.
Before you tag:

1. **Bump the version** in each client that has changes:
   - Python: `src/kyccentral/_version.py` (single `__version__` string)
   - JavaScript: `version` field in `javascript/package.json`
   - Elixir: `@version` in `elixir/mix.exs`
2. **Update the changelogs**: move the `## Unreleased` entries under a new
   `## X.Y.Z — YYYY-MM-DD` heading in each changed client's `CHANGELOG.md`.
3. **Commit** with a message like `Release vX.Y.Z`.
4. **Tag** and **push** the tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

The `publish.yml` workflow starts automatically. It checks each of the three
directories for changes since the previous `v*` tag; any that changed get their full
test + lint + format + type-check suite run, and on green, the package is published.

> **To force-publish everything** (e.g. a version bump with no code changes): delete
> the previous tag and retag, or push a new tag — the workflow treats the first tag
> ever as "everything changed".

## What the publish workflow does per language

| Language | Build | Publish | Auth |
|---|---|---|---|
| Python | `python -m build` → `python/dist/` | `pypa/gh-action-pypi-publish` | OIDC trusted publishing |
| JavaScript | `npm run build` (tsup: ESM + CJS + .d.ts) | `npm publish --provenance` | OIDC trusted publishing |
| Elixir | `mix compile` (via `mix hex.publish`) | `mix hex.publish --yes` | `HEX_API_KEY` |

## Verifying a release

Wait 5–10 minutes, then check:

- PyPI: <https://pypi.org/project/kyccentral/>
- npm: <https://www.npmjs.com/package/@kyccentral/sdk>
- Hex: <https://hex.pm/packages/kyccentral>

## Notes

- **npm trusted publishing**: the `id-token: write` permission lets npm exchange the
  GitHub OIDC token for a short-lived npm token — no `NPM_TOKEN` secret is stored. The
  workflow strips setup-node's empty `_authToken` line from `.npmrc` so the npm CLI
  initiates the OIDC exchange instead of failing with `ENEEDAUTH`. `--provenance`
  (also set in `package.json`) generates an [SLSA](https://slsa.dev/) attestation linking
  the package to this repo and the release tag; npm shows a "View transparency details"
  link on the package page. Requires npm CLI 11.5.1+ (Node 22.14+; the workflow uses
  Node 24).
- **PyPI trusted publishing**: requires the tag to be pushed from the default branch
  (`main`). If you publish from a fork, use an API token instead.
- **Hex key**: rotate this just like any other secret; `HEX_API_KEY` is not tied to a
  specific version.
- **Version bump discipline**: even if only one language changed, bump only that one's
  version. The publish workflow skips clients whose directory is unchanged since the
  previous tag.
