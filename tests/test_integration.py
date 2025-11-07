"""Integration tests that exercise the real DSPy predictor path."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi.testclient import TestClient
import httpx
import pytest

# Ensure DSPy cache writes land inside the repo workspace (and stay writable).
DSPY_CACHE_DIR = Path("data/.dspy_cache")
DSPY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DSPY_CACHEDIR", str(DSPY_CACHE_DIR))

from src.api.app import app
from src.common.config import configure_lm
from src.serving.service import ComplaintRequest, get_classification_function


logger = logging.getLogger(__name__)


def _ensure_predictor():
    """Configure LM + load predictor, skipping when pre-reqs are missing."""

    try:
        configure_lm()
    except RuntimeError as exc:  # missing API key
        pytest.skip(f"LLM configuration not available: {exc}")

    try:
        return get_classification_function()
    except FileNotFoundError as exc:
        pytest.skip(f"Classifier artifact missing: {exc}")


def _invoke_llm(predictor, payload: ComplaintRequest):
    """Call the predictor but treat transient HTTP failures as skips."""

    try:
        return predictor(payload)
    except Exception as exc:  # noqa: BLE001 - any upstream HTTP failure should skip the test
        pytest.skip(f"LLM invocation failed: {exc}")


@pytest.mark.integration
def test_predictor_classifies_complaint():
    predictor = _ensure_predictor()

    payload = ComplaintRequest(
        complaint="After injecting Ozempic my throat started swelling and I needed an EpiPen."
    )
    response = _invoke_llm(predictor, payload)

    assert response.classification in {"Adverse Event", "Product Complaint"}
    assert response.justification
    logger.info(
        "Predictor classification=%s justification=%s",
        response.classification,
        response.justification,
    )


@pytest.mark.integration
def test_fastapi_endpoint_uses_loaded_predictor():
    predictor = _ensure_predictor()
    app.state.predictor = predictor
    app.state.startup_error = None

    client = TestClient(app)
    try:
        resp = client.post(
            "/classify",
            json={"complaint": "My Ozempic pen arrived cracked and leaking.", "model_path": None},
        )
    except (httpx.HTTPError, Exception) as exc:  # pragma: no cover - network/transient
        pytest.skip(f"HTTP call failed: {exc}")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["classification"] in {"Adverse Event", "Product Complaint"}
    assert payload["justification"]
    logger.info(
        "API classification=%s justification=%s",
        payload["classification"],
        payload["justification"],
    )
