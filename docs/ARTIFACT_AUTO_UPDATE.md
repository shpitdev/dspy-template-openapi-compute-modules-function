# Automatic Artifact Metadata Update

## Overview

Starting with this update, artifact metadata (specifically the `model` field) is automatically updated when classifiers are loaded. This ensures that artifacts stay synchronized with the current environment configuration without requiring full retraining.

## The Problem

Previously, if you:
1. Trained a classifier with model A → artifact saved with `"model": "A"`
2. Changed your environment to use model B
3. Used the existing artifact

The artifact metadata would still show model A, even though you're now using model B. This could cause confusion, especially when deploying to Cloudflare Workers or other environments that read the model metadata.

## The Solution

Now, whenever a classifier artifact is loaded (via `_load_classifier()` in `src/serving/service.py`), the code:

1. Checks the current model from `dspy.settings.lm.model`
2. Compares it to the saved model in `artifact['metadata']['model']`
3. If they differ, updates the artifact metadata with the current model
4. Saves the updated artifact back to disk

This happens automatically and transparently during:
- Inference runs (`inference_demo.py`)
- API server startup (`src/api/app.py`)
- Any code that loads classifiers via the serving layer

## Example

```python
# Initial state: artifact has old model
$ cat artifacts/ozempic_classifier_ae-pc_optimized.json | grep model
"model": "openrouter/openai/gpt-oss-20b"

# Configure new model
$ export DSPY_MODEL_NAME="Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL"
$ export DSPY_PROVIDER="local"

# Run inference (or start API, or load classifier)
$ python inference_demo.py

# After loading: artifact has new model
$ cat artifacts/ozempic_classifier_ae-pc_optimized.json | grep model
"model": "openai/Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL.gguf"
```

## Benefits

- ✅ **No manual editing**: Artifacts are read-only from user perspective
- ✅ **No retraining needed**: Just to update metadata
- ✅ **Automatic**: Happens transparently on next run
- ✅ **Safe**: Preserves all other metadata fields
- ✅ **Robust**: Silently continues if file I/O fails

## Implementation Details

**Location**: `src/serving/service.py::_load_classifier()`

**Logic**:
```python
current_model = dspy.settings.lm.model if dspy.settings.lm else None
if current_model:
    saved_model = artifact_data.get("metadata", {}).get("model")
    if saved_model != current_model:
        artifact_data["metadata"]["model"] = current_model
        # Save updated artifact
```

**Error Handling**: 
- Wrapped in try/except for OSError and JSONDecodeError
- Failures don't crash the application
- Classifier still loads and works even if metadata update fails

## Testing

Run the test suite to verify the functionality:

```bash
pytest tests/test_artifact_metadata_update.py -v
```

Or run the demonstration script:

```bash
python scripts/demo_artifact_auto_update.py
```

## When It Runs

The auto-update happens when:
1. Loading classifiers for inference
2. Starting the FastAPI server
3. Running the demo scripts
4. Any code path that calls `_load_classifier()`

It does NOT happen during:
- Initial training/optimization (that saves the current model anyway)
- Just reading artifact files
- Deployment script generation (reads but doesn't load classifiers)

## Migration Notes

If you have old artifacts with outdated model metadata:
1. Simply configure your desired model in the environment
2. Run any code that loads the classifier (e.g., `inference_demo.py`)
3. The metadata will be automatically updated

No manual intervention required!
