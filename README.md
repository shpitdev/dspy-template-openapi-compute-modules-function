# DSPy Reference Examples

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://docs.python.org/3/)
[![DSPy](https://img.shields.io/badge/DSPy-3.1.0-1F2937)](https://dspy.ai/)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.72.6-00A67E)](https://docs.litellm.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.12.5-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/latest/)
[![Ruff](https://img.shields.io/badge/Ruff-0.14.10-FCC21B?logo=ruff&logoColor=000000)](https://docs.astral.sh/ruff/)
[![uv](https://img.shields.io/badge/uv-0.9.18-0E6F5A)](https://docs.astral.sh/uv/)

**Models:**
[![Nemotron-3-Nano-30B](https://img.shields.io/badge/Nemotron--3--Nano--30B-HF_(unsloth_quantized)-76B900?logo=nvidia&logoColor=white)](https://huggingface.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF)
[![GPT-OSS-120B](https://img.shields.io/badge/openai/gpt--oss--120b-OpenRouter_(Cerebras)-F76B1C?logo=openai&logoColor=white)](https://openrouter.ai/openai/gpt-oss-120b?sort=throughput)

Real-world DSPy workflows for pharma/medtech teams. This project provides a flexible multi-classification system for
Ozempic-related text analysis. Currently supports three classification tasks:

1. **AE vs PC Detection** - Distinguish Adverse Events from Product Complaints
2. **AE Category Classification** - Categorize adverse events into specific medical categories
3. **PC Category Classification** - Categorize product complaints into specific quality categories

The framework shows how to:

- Programmatically optimize prompts with DSPy
- Support multiple classification tasks with dynamic signatures
- Persist tuned artifacts to disk (separate from source)
- Serve classifiers via FastAPI with typed Pydantic contracts

---

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) for env + dependency management (no `pip`/`poetry`)
- OpenAI-compatible API key
  - Default provider: [OpenRouter](https://openrouter.ai/) using `nvidia/nemotron-3-nano-30b-a3b:free`
  - Override via environment variables without touching code

### Environment variables

| Variable                                          | Description                      | Default                        |
| ------------------------------------------------- | -------------------------------- | ------------------------------ |
| `OPENROUTER_API_KEY`                              | Primary key for OpenRouter       | —                              |
| `OPENAI_API_KEY` / `DSPY_API_KEY`                 | Override for OpenAI/custom key   | —                              |
| `DSPY_MODEL_NAME`                                 | Model ID                         | `nvidia/nemotron-3-nano-30b-a3b:free` |
| `DSPY_LOCAL_BASE`                                 | Base URL for local provider      | `http://localhost:8080/v1`     |
| `DSPY_HTTP_HEADERS`                               | JSON blob for extra HTTP headers | `{}`                           |
| `OPENROUTER_HTTP_REFERER`, `OPENROUTER_APP_TITLE` | OpenRouter analytics headers     | —                              |
| `DSPY_LOG_LEVEL`                                  | Log verbosity                    | `INFO`                         |
| `DSPY_LOG_FORMAT`                                 | Log format (`json` or `text`)    | `json`                         |
| `DSPY_RUN_ID`                                     | Correlation run id               | auto-generated                 |
| `DSPY_ARTIFACT_AUTO_UPDATE`                       | Auto-update artifact model metadata on load | `false`             |

Copy `.env.example` and fill in whichever keys you need:

```bash
cp .env.example .env
```

---

## Project Setup

```bash
uv sync --extra dev
```
```bash
source .venv/bin/activate
```

# Generate training data for all classification types
```bash
uv run python scripts/datagen/adverse_event_sample_data.py
uv run python scripts/datagen/complaint_category_sample_data.py
uv run python scripts/datagen/ae_pc_classification_sample_data.py
```

This creates a clean layout:

```text
.
├── artifacts/                           # Saved DSPy artifacts (git-tracked)
│   ├── ozempic_classifier_ae-pc_optimized.json
│   ├── ozempic_classifier_ae-category_optimized.json
│   └── ozempic_classifier_pc-category_optimized.json
├── data/                                # Synthetic train/test data organized by task
│   ├── ae-pc-classification/            # AE vs PC detection
│   │   ├── train.json
│   │   └── test.json
│   ├── ae-category-classification/      # AE category classification
│   │   ├── train.json
│   │   └── test.json
│   └── pc-category-classification/      # PC category classification
│       ├── train.json
│       └── test.json
├── scripts/
│   ├── datagen/                         # Data generation scripts
│   └── deploy/                          # Deployment scripts
├── src/
│   ├── api/                             # FastAPI app
│   ├── common/                          # Shared logic (config, datasets, classifier)
│   ├── pipeline/                        # Optimization pipeline
│   └── serving/                         # Pydantic request/response + helpers
└── inference_demo.py                    # Simple batch inference helper
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

Train a classifier for a specific task using the `--classification-type` flag:

### Train AE vs PC classifier (default)
```bash
uv run python -m src.pipeline.main --classification-type ae-pc
```

### Train AE category classifier
```bash
uv run python -m src.pipeline.main --classification-type ae-category
```

### Train PC category classifier
```bash
uv run python -m src.pipeline.main --classification-type pc-category
```

The run will:

1. Configure DSPy with your provider settings.
2. Load the appropriate `data/<type>-classification/train.json` and `test.json`.
3. Evaluate the baseline classifier.
4. Optimize via `MIPROv2` (with `auto="medium"`).
5. Evaluate the optimized program.
6. Write the artifact to `artifacts/ozempic_classifier_<type>_optimized.json`.


---

## 2. Serve the Classifier via FastAPI

```bash
uv run uvicorn src.api.app:app --reload
```

- API Root: `http://localhost:8000/` (shows available endpoints)
- Swagger/OpenAPI UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`
- Health endpoint: `GET /health`

### Classification Endpoints

The API provides three classification endpoints:

1. **`POST /classify/ae-pc`** - Classify as Adverse Event or Product Complaint (first-stage classification)
2. **`POST /classify/ae-category`** - Classify adverse events into specific medical categories (e.g., Gastrointestinal
   disorders, Pancreatitis, Hypoglycemia)
3. **`POST /classify/pc-category`** - Classify product complaints into quality/defect categories (e.g., Device
   malfunction, Packaging defect)

#### Example: AE vs PC Classification

```bash
curl -X POST http://localhost:8000/classify/ae-pc \
     -H "Content-Type: application/json" \
     -d '{
           "complaint": "After injecting Ozempic I had severe hives and needed an EpiPen."
         }'
```

Response:

```json
{
  "classification": "Adverse Event",
  "justification": "Describes a systemic allergic reaction following Ozempic use.",
  "classification_type": "ae-pc"
}
```

#### Example: AE Category Classification

```bash
curl -X POST http://localhost:8000/classify/ae-category \
     -H "Content-Type: application/json" \
     -d '{
          "complaint": "I experienced severe nausea and vomiting after taking Ozempic."
         }'
```

#### Example: PC Category Classification

```bash
curl -X POST http://localhost:8000/classify/pc-category \
     -H "Content-Type: application/json" \
     -d '{
          "complaint": "The pen arrived with a cracked dose dial."
         }'
```

If an artifact is missing, the API returns `503 Service Unavailable` with instructions to rerun the pipeline.

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

The container always starts via `uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}`, matching the local dev
commands.

---

## Local LLM Server (llama.cpp)

To run a local LLM server using llama.cpp:

```bash
cd llama.cpp

# Build llama.cpp
cmake -B build
cmake --build build --config Release

# Download the model from Hugging Face (save to models directory)
# Visit the model page on HF for the curl command, e.g.:
# curl -L -o models/Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL.gguf <HF_URL>
```

### Start the server
```bash
./serve.sh -m ~/llama.cpp/models/Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL.gguf
```

### Then configure DSPy to use your local server by setting:
```bash
export DSPY_LOCAL_BASE=http://localhost:8080/v1
export DSPY_MODEL_NAME=local-model
```

---

## Notes & Next Steps

- Replace `data/*-classification/*.json` with real labeled datasets or update `src/common/data_utils.py` to read from
  your storage systems.
- Add new classification types by:
  1. Adding a new entry to `CLASSIFICATION_CONFIGS` in `src/common/classifier.py`
  2. Adding a new entry to `CLASSIFICATION_TYPES` in `src/common/paths.py`
  3. Creating training data scripts in `scripts/datagen/`
  4. Training with `--classification-type <new-type>`
- Add additional pipelines (extraction, severity grading, etc.) by following the same pattern: shared logic in
  `src/common`, tuning flows in `src/pipeline`, serving code in `src/api`/`src/serving`.
- The LM client is OpenAI-compatible; switching to Anthropic, Azure OpenAI, or self-hosted proxies is just a matter of
  environment variables.

---

## License

MIT – see `LICENSE` for details.
