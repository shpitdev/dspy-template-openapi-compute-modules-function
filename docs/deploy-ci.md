# Deployment Automation (Railway + Foundry)

This repository now ships CI/CD workflows that validate one container contract and publish immutable images for both Railway-compatible and Foundry registries.

Verification note: workflow chain was validated end-to-end on 2026-02-14.

## Workflows

- `.github/workflows/ci.yml`
  - Runs on pull requests and pushes to `main`.
  - Executes test suite, Foundry OpenAPI validation, image metadata validation, and Docker portability smoke (`PORT=8080` and `PORT=5000`).
- `.github/workflows/publish-platform-images.yml`
  - Runs on pushes to `main` (and manual dispatch).
  - Builds one linux/amd64 image and pushes immutable tags to:
    - `ghcr.io/<owner>/<repo>`
    - `<FOUNDRY_REGISTRY_HOST>/<FOUNDRY_DOCKER_IMAGE_NAME>`
- `.github/workflows/release-version.yml`
  - After successful `CI` on `main`, automatically bumps patch version in `pyproject.toml`, creates a `vX.Y.Z` git tag, and triggers a Foundry + GHCR publish for that release.
- `.github/workflows/railway-preview-smoke.yml`
  - Runs on successful preview `deployment_status` events (or manual dispatch).
  - Resolves preview URL and runs deployed smoke tests from `tests/routes`.
- `.github/workflows/railway-production-smoke.yml`
  - Runs on successful non-transient production `deployment_status` events (or manual dispatch).
  - Resolves production URL and runs deployed smoke tests from `tests/routes`.

## Required Secrets

- `FOUNDRY_REGISTRY_HOST`
- `FOUNDRY_DOCKER_IMAGE_NAME`
- `FOUNDRY_ARTIFACT_REPOSITORY_RID`
- `FOUNDRY_TOKEN`

## Required Repository Variable

- `RAILWAY_SERVICE_SLUG` (optional if it matches repository name)

## Quick GitHub Secret Setup

If you already have local shell exports for Foundry auth:

```bash
# Example exports:
# export REPOSITORY=ri.artifacts.main.repository.<your-rid>
# export TOKEN=<short-lived-foundry-registry-token>
#
# Also set these:
# export FOUNDRY_REGISTRY_HOST=<stack>-container-registry.palantirfoundry.com
# export FOUNDRY_DOCKER_IMAGE_NAME=<your-image-path>
# export RAILWAY_SERVICE_SLUG=<your-railway-service-slug>

gh secret set FOUNDRY_ARTIFACT_REPOSITORY_RID --body "$REPOSITORY"
gh secret set FOUNDRY_TOKEN --body "$TOKEN"
gh secret set FOUNDRY_REGISTRY_HOST --body "$FOUNDRY_REGISTRY_HOST"
gh secret set FOUNDRY_DOCKER_IMAGE_NAME --body "$FOUNDRY_DOCKER_IMAGE_NAME"
gh variable set RAILWAY_SERVICE_SLUG --body "$RAILWAY_SERVICE_SLUG"
```

Mapping:
- `REPOSITORY` -> `FOUNDRY_ARTIFACT_REPOSITORY_RID`
- `TOKEN` -> `FOUNDRY_TOKEN`

`FOUNDRY_TOKEN` is short-lived. Plan to refresh and reset this secret before each publish window.

## Foundry Runtime Notes

- Foundry OpenAPI contract is generated to `openapi.foundry.json` and validated with server URL `http://localhost:5000`.
- Container runs as numeric non-root user `5000:5000`.
- Image label `server.openapi` is required and must exactly match `openapi.foundry.json`.
- Foundry registry should primarily use version tags (e.g. `0.1.2`) rather than `main-...` tags.

For a short explanation of the "OpenAPI -> functions" import path (plus screenshots), see `docs/foundry-auto-deploy.md`.

## Railway Runtime Notes

- Runtime continues to honor `PORT` with default `8080`.
- Portability smoke tests verify both Railway-like (`8080`) and Foundry-like (`5000`) runtime profiles.
- Deployment-status workflows derive URL as `https://<service-slug>-<environment-slug>.up.railway.app` unless manually overridden.
