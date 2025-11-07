"""FastAPI application that exposes the optimized classifier."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from ..common.config import configure_lm
from ..serving.service import (
    ComplaintRequest,
    ComplaintResponse,
    get_classification_function,
)

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Load the predictor at startup so TestClient + ASGI servers share logic."""

    configure_lm()
    try:
        app.state.predictor = get_classification_function()
        app.state.startup_error = None
    except FileNotFoundError as exc:
        app.state.predictor = None
        app.state.startup_error = exc
    yield


app = FastAPI(
    title="DSPy Complaint Classifier API",
    version="0.2.0",
    description=(
        "Classify Ozempic-related complaints as Adverse Events or Product Complaints. "
        "Run the optimization pipeline to refresh the underlying prompt artifact."
    ),
    lifespan=_lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", tags=["system"], summary="API Root")
def root() -> dict[str, str]:
    """Root endpoint with API information and links to documentation."""
    return {
        "name": "DSPy Complaint Classifier API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", tags=["system"], summary="Health check")
def healthcheck() -> dict[str, str]:
    if getattr(app.state, "predictor", None) is None:
        if getattr(app.state, "startup_error", None):
            return {"status": "degraded", "detail": "Model artifact missing"}
        return {"status": "initializing"}
    return {"status": "ok"}


@app.post(
    "/classify",
    response_model=ComplaintResponse,
    summary="Classify an Ozempic complaint",
    tags=["classification"],
)
def classify(payload: ComplaintRequest) -> ComplaintResponse:
    predictor = getattr(app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Classifier artifact not loaded. Run the optimization pipeline "
                "or ensure the artifact exists in the artifacts directory."
            ),
        )
    return predictor(payload)


__all__ = ["app"]
