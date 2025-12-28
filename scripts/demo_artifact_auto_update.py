#!/usr/bin/env python3
"""
Demonstration of automatic artifact metadata update.

This script demonstrates how artifacts are automatically updated with the current 
model metadata when they are loaded, without requiring a full retraining.

Run this to see the auto-update in action:
    python scripts/demo_artifact_auto_update.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Set up environment to use local provider
os.environ["DSPY_PROVIDER"] = "local"
os.environ["DSPY_MODEL_NAME"] = "Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL"

from src.common.config import configure_lm
from src.common.paths import get_classifier_artifact_path

print("=" * 70)
print("ARTIFACT METADATA AUTO-UPDATE DEMONSTRATION")
print("=" * 70)

# Configure the language model
print("\n1. Configuring language model...")
try:
    lm = configure_lm()
    print(f"   ✓ LM configured: {lm.model}")
except Exception as e:
    print(f"   ⚠️  LM configuration failed (expected if server not running): {e}")
    print("   This demo will show the concept even without a running server.")

import dspy

current_model = getattr(dspy.settings.lm, "model", None) or "openai/Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL.gguf"
print(f"   Current model in environment: {current_model}")

# Check artifacts before loading
print("\n2. Checking artifact metadata BEFORE loading...")
classification_types = ["ae-pc", "ae-category", "pc-category"]

before_models = {}
for classification_type in classification_types:
    artifact_path = get_classifier_artifact_path(classification_type)
    with open(artifact_path) as f:
        data = json.load(f)
    
    model = data.get("metadata", {}).get("model", "NO MODEL")
    before_models[classification_type] = model
    
    status = "✓" if "nemotron" in model.lower() else "⚠️"
    print(f"   {status} {classification_type}: {model}")

print("\n3. Loading classifiers (this triggers auto-update if model differs)...")
print("   Note: This would normally load and use the classifier.")
print("   The load operation checks if the saved model differs from the current")
print("   environment model, and if so, automatically updates the artifact metadata.")

# For demonstration, we'll just show what would happen
print("\n4. What happens during load:")
print("   a) Classifier loads the artifact")
print("   b) Code checks: saved_model != current_model?")
print("   c) If different: Update metadata['model'] = current_model")
print("   d) Save updated artifact back to disk")
print("   e) Return loaded classifier")

print("\n5. Key benefits of auto-update:")
print("   • No manual editing of artifacts required")
print("   • No full retraining needed just to update metadata")
print("   • Artifacts stay synchronized with environment")
print("   • Works transparently on next inference/API run")

print("\n6. When does auto-update happen?")
print("   • When loading a classifier via service.py")
print("   • When running inference_demo.py")
print("   • When starting the FastAPI server")
print("   • Any time _load_classifier() is called")

print("\n7. Implementation details:")
print("   • Located in: src/serving/service.py::_load_classifier()")
print("   • Checks: dspy.settings.lm.model != artifact['metadata']['model']")
print("   • Preserves: All other metadata fields")
print("   • Error handling: Silently continues if file I/O fails")

print("\n" + "=" * 70)
print("For a full demonstration:")
print("  1. Configure a model: export DSPY_MODEL_NAME='your-model'")
print("  2. Run inference: python inference_demo.py")
print("  3. Check artifacts: they'll have the updated model metadata")
print("=" * 70)
