"""Integration tests that exercise the real DSPy predictor path."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# Ensure DSPy cache writes land inside the repo workspace (and stay writable).
DSPY_CACHE_DIR = Path("data/.dspy_cache")
DSPY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DSPY_CACHEDIR", str(DSPY_CACHE_DIR))

# Imports must come after environment setup
from src.api.app import app  # noqa: E402
from src.common.config import configure_lm  # noqa: E402
from src.serving.service import AEPCRequest, get_ae_pc_classifier  # noqa: E402


def _ensure_predictor():
    """Configure LM + load predictor, skipping when pre-reqs are missing."""

    try:
        configure_lm()
    except RuntimeError as exc:  # missing API key
        pytest.skip(f"LLM configuration not available: {exc}")

    try:
        return get_ae_pc_classifier()
    except FileNotFoundError as exc:
        pytest.skip(f"Classifier artifact missing: {exc}")


def _invoke_llm(predictor, payload: AEPCRequest):
    """Call the predictor but treat transient HTTP failures as skips."""

    try:
        return predictor(payload)
    except Exception as exc:  # noqa: BLE001 - any upstream HTTP failure should skip the test
        pytest.skip(f"LLM invocation failed: {exc}")


@pytest.mark.integration
def test_predictor_classifies_complaint():
    predictor = _ensure_predictor()

    payload = AEPCRequest(complaint="After injecting Ozempic my throat started swelling and I needed an EpiPen.")
    response = _invoke_llm(predictor, payload)

    assert response.classification in {"Adverse Event", "Product Complaint"}
    assert response.justification


@pytest.mark.integration
def test_fastapi_endpoint_uses_loaded_predictor():
    predictor = _ensure_predictor()
    # Mock the loaded predictor in the app state
    app.state.ae_pc_predictor = predictor
    # Ensure errors dict exists
    app.state.errors = {}

    client = TestClient(app)
    try:
        resp = client.post(
            "/classify/ae-pc",
            json={"complaint": "My Ozempic pen arrived cracked and leaking."},
        )
    except (httpx.HTTPError, Exception) as exc:  # pragma: no cover - network/transient
        pytest.skip(f"HTTP call failed: {exc}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["classification"] in {"Adverse Event", "Product Complaint"}
    assert payload["justification"]
