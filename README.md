# DSPy Reference Examples

Real-world DSPy workflows for pharma/medtech teams. The current module focuses on Ozempic complaint triage (Adverse
Event vs Product Complaint) and shows how to:

- Programmatically optimize a prompt with DSPy
- Persist the tuned artifact to disk (separate from source)
- Serve the classifier via FastAPI with typed Pydantic contracts

---

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) for env + dependency management (no `pip`/`poetry`)
- OpenAI-compatible API key
  - Default provider: [OpenRouter](https://openrouter.ai/) using `openai/gpt-oss-120b`
  - Override via environment variables without touching code

### Environment variables

| Variable                                          | Description                      | Default                        |
| ------------------------------------------------- | -------------------------------- | ------------------------------ |
| `OPENROUTER_API_KEY`                              | Primary key for OpenRouter       | —                              |
| `OPENAI_API_KEY` / `DSPY_API_KEY`                 | Override for OpenAI/custom key   | —                              |
| `DSPY_MODEL_NAME`                                 | Model ID                         | `openai/gpt-oss-120b`          |
| `DSPY_API_BASE`                                   | Base URL for model provider      | `https://openrouter.ai/api/v1` |
| `DSPY_HTTP_HEADERS`                               | JSON blob for extra HTTP headers | `{}`                           |
| `OPENROUTER_HTTP_REFERER`, `OPENROUTER_APP_TITLE` | OpenRouter analytics headers     | —                              |

Copy `.env.example` and fill in whichever keys you need:

```bash
cp .env.example .env
```

---

## Project Setup

```bash
uv sync                     # creates/updates .venv from pyproject + uv.lock
source .venv/bin/activate
uv run python scripts/generate_sample_data_ozempic_pc_vs_ae.py  # creates data/train.json & data/test.json
```

This creates a clean layout:

```text
.
├── artifacts/                      # Saved DSPy artifacts (git-tracked)
├── data/                           # Synthetic train/test data
├── scripts/                        # Utility scripts (data generation)
├── src/
│   ├── api/                        # FastAPI app
│   ├── common/                     # Shared logic (config, datasets, classifier)
│   ├── pipeline/                   # Optimization pipeline
│   └── serving/                    # Pydantic request/response + helpers
└── inference_demo.py               # Simple batch inference helper
```

### Code Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both formatting and linting (line length: 120).

**Format and fix all issues:**

```bash
uv run ruff format .              # Format all Python files
uv run ruff check --fix .         # Fix all auto-fixable linting issues
```

**Check for issues without fixing:**

```bash
uv run ruff check .               # Check for linting issues
uv run ruff format --check .      # Check formatting without changing files
```

**Note:** Ruff's formatter preserves triple-quoted strings (`"""`) as-is by design. For files with long triple-quoted
strings (like data generation scripts), you may need to manually wrap them if desired.

**VSCode users:** Format on save is enabled by default using Ruff. Install the recommended extensions (Python, Ruff)
when prompted.

---

## 1. Optimize / Refresh the Classifier

```bash
uv run python -m src.pipeline.main
```

The run will:

1. Configure DSPy with your provider settings.
2. Load `data/train.json` / `data/test.json`.
3. Evaluate the baseline classifier.
4. Optimize via `BootstrapFewShotWithRandomSearch`.
5. Evaluate the optimized program.
6. Write the artifact to `artifacts/ozempic_classifier_optimized.json`.

Running the pipeline is idempotent—rerun whenever you update data or want to swap underlying LMs.

---

## 2. Serve the Classifier via FastAPI

```bash
uv run uvicorn src.api.app:app --reload
```

- Swagger/OpenAPI UI: `http://localhost:8000/docs`
- Health endpoint: `GET /health`
- Classification endpoint: `POST /classify` (uses the same Pydantic models as the internal service layer)

Example request body (auto-populated in Swagger):

```json
{
  "complaint": "My Ozempic pen arrived cracked and leaked everywhere.",
  "model_path": null
}
```

Example `curl` invocation:

```bash
curl -X POST http://localhost:8000/classify \
     -H "Content-Type: application/json" \
     -d '{
           "complaint": "After injecting Ozempic I had severe hives and needed an EpiPen.",
           "model_path": null
         }'
```

Response structure:

```json
{
  "classification": "Adverse Event",
  "justification": "Describes a systemic allergic reaction following Ozempic use."
}
```

If the artifact is missing, the API returns `503 Service Unavailable` with instructions to rerun the pipeline.

---

## 3. Use the Pydantic Interface Directly

```python
from src.common.config import configure_lm
from src.serving.service import ComplaintRequest, get_classification_function

configure_lm()
predict = get_classification_function()

payload = ComplaintRequest(complaint="Pen arrived with a broken dose dial.")
result = predict(payload)
print(result.classification, result.justification)
```

Pass `model_path="artifacts/ozempic_classifier_optimized.json"` (or another artifact) to pin a different tuned model per
tenant or use-case.

---

## Demo Script

`uv run python inference_demo.py` executes a small batch of complaints through the shared interface and prints
latency/throughput stats. Useful for quick smoke tests after retraining.

---

## 4. Docker & Railway Deployment

### Build & Run Locally

```bash
docker build -t dspy-reference .
docker run --rm \
  --env-file .env \
  -p 8080:8080 \
  -v "$(pwd)/data:/data" \
  dspy-reference
```

- The image uses the pre-baked `.venv` from `uv sync --frozen --no-dev` and serves FastAPI on `0.0.0.0:8080`.
- Mount `$(pwd)/data` to `/data` when you need persistence (e.g., refreshed artifacts, uploads, sqlite files).
- Override the port by passing `-e PORT=9000`; the default command reads `PORT` and falls back to `8080`.

### Deploy to Railway

1. Push this repo (with the Dockerfile) to GitHub and create a Railway project using the Docker template.
2. In the Railway dashboard, set the required env vars (`OPENROUTER_API_KEY`, `DSPY_MODEL_NAME`, etc.). Railway
   automatically sets `PORT`; no build args are needed.
3. Attach a persistent volume mounted at `/data` if you need on-disk artifacts or databases.
4. Each deploy builds directly from the Dockerfile’s multi-stage workflow; use `railway up` or manual deploys after
   committing changes.

The container always starts via `uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8080}`, matching the local dev
commands.

---

## Notes & Next Steps

- Replace `data/*.json` with real labeled datasets or update `src/common/data_utils.py` to read from your storage
  systems.
- Add additional pipelines (extraction, severity grading, etc.) by following the same pattern: shared logic in
  `src/common`, tuning flows in `src/pipeline`, serving code in `src/api`/`src/serving`.
- The LM client is OpenAI-compatible; switching to Anthropic, Azure OpenAI, or self-hosted proxies is just a matter of
  environment variables.

---

## License

MIT – see `LICENSE` for details.
