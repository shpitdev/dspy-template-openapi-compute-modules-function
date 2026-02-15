# Foundry OpenAPI Deployment Runbook

This runbook captures the full M1-M7 flow for the FastAPI compute module import path.

For the conceptual overview and screenshots of the import UX, see `docs/foundry-auto-deploy.md`.

## Locked Targets

- `FOUNDRY_URL=https://23dimethyl.usw-3.palantirfoundry.com`
- `COMPUTE_MODULE_RID=ri.foundry.main.deployed-app.72637ae9-ceb5-4fdc-890f-10fdbfe72db0`
- `FOUNDRY_REPOSITORY=pharma-classifier-dspy`
- `FOUNDRY_PROJECT_PATH=/23dimethyl-7809be/Open Ontology (ontologydev.com)/tutorials/dspy-reference-examples`

## Image Naming Contract

- Use immutable tags only (no `latest`)
- Recommended tag format: `YYYYMMDD-HHMMSS-<gitsha7>`
- Image ref format: `${REGISTRY_HOST}/${FOUNDRY_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}`

## M1-M3: Generate Constrained OpenAPI

```bash
uv run python scripts/deploy/foundry_openapi.py --generate --spec-path openapi.foundry.json
uv run python scripts/deploy/foundry_openapi.py --spec-path openapi.foundry.json
```

Resulting contract contains only:

- `POST /classify/ae-pc` (`operationId=classifyAePc`)
- `POST /classify/ae-category` (`operationId=classifyAeCategory`)
- `POST /classify/pc-category` (`operationId=classifyPcCategory`)
- `servers = [{"url":"http://localhost:5000"}]`

## M4-M6: Build + Validate Image Metadata

```bash
export REGISTRY_HOST="<from Foundry Container tab>"
export IMAGE_NAME="dspy-reference-examples"
export IMAGE_TAG="$(date -u +%Y%m%d-%H%M%S)-$(git rev-parse --short HEAD)"
export IMAGE_REF="${REGISTRY_HOST}/${FOUNDRY_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"
```

```bash
export OPENAPI_JSON="$(uv run python -c 'import json; print(json.dumps(json.load(open("openapi.foundry.json")), separators=(",", ":")))')"
docker buildx build \
  --platform linux/amd64 \
  --build-arg SERVER_OPENAPI="${OPENAPI_JSON}" \
  --tag "${IMAGE_REF}" \
  --load \
  .
```

```bash
uv run python scripts/deploy/foundry_openapi.py \
  --spec-path openapi.foundry.json \
  --image-ref "${IMAGE_REF}"
```

Optional local runtime smoke test (non-production):

```bash
docker run --rm -d --name dspy-foundry-check -e DSPY_PROVIDER=local -e PORT=5000 -p 15000:5000 "${IMAGE_REF}"
sleep 4
curl -sSf http://127.0.0.1:15000/health
docker rm -f dspy-foundry-check
```

## M7: Push + Import Sequence

```bash
export FOUNDRY_REGISTRY_USER="<from Foundry Container tab>"
export FOUNDRY_REGISTRY_TOKEN="<short-lived token from Foundry Container tab>"
echo "${FOUNDRY_REGISTRY_TOKEN}" | docker login "${REGISTRY_HOST}" --username "${FOUNDRY_REGISTRY_USER}" --password-stdin
docker push "${IMAGE_REF}"
```

Then complete UI-only steps in Foundry:

1. Open compute module `${COMPUTE_MODULE_RID}`.
2. Link container image `${IMAGE_REF}` from repository `${FOUNDRY_REPOSITORY}`.
3. Run `Detect from OpenAPI specification`.
4. Confirm the three imported functions map to the three classify routes.
5. Save and publish.

## Remaining Human Blockers

- H1: Provide `REGISTRY_HOST`, `FOUNDRY_REGISTRY_USER`, and short-lived token.
- H2: Execute image-link and OpenAPI detect/import UI actions.
- H3: Configure egress to `openrouter.ai:443` and secret mapping for `OPENROUTER_API_KEY`.
- H4: Run final smoke tests from Foundry function endpoints.
