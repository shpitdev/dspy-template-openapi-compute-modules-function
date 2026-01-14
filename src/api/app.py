"""FastAPI application that exposes the optimized classifier."""

from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from loguru import logger

from ..common.config import configure_lm
from ..common.types import ClassificationType
from ..serving.service import (
    AECategoryRequest,
    AEPCRequest,
    ComplaintResponse,
    PCCategoryRequest,
    get_ae_category_classifier,
    get_ae_pc_classifier,
    get_pc_category_classifier,
)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    configure_lm()

    app.state.errors = {}

    try:
        app.state.ae_pc_predictor = get_ae_pc_classifier()
    except FileNotFoundError as exc:
        app.state.ae_pc_predictor = None
        app.state.errors[ClassificationType.AE_PC] = str(exc)

    try:
        app.state.ae_category_predictor = get_ae_category_classifier()
    except FileNotFoundError as exc:
        app.state.ae_category_predictor = None
        app.state.errors[ClassificationType.AE_CATEGORY] = str(exc)

    try:
        app.state.pc_category_predictor = get_pc_category_classifier()
    except FileNotFoundError as exc:
        app.state.pc_category_predictor = None
        app.state.errors[ClassificationType.PC_CATEGORY] = str(exc)

    yield


app = FastAPI(
    title="DSPy Complaint Classifier API",
    version="0.3.0",
    description=(
        "Multi-stage complaint classification API for Ozempic-related issues. "
        "Supports three classification types:\n\n"
        "1. **AE vs PC**: Classify as Adverse Event or Product Complaint\n"
        "2. **AE Category**: Classify adverse events into specific medical categories\n"
        "3. **PC Category**: Classify product complaints into specific quality/defect categories\n\n"
        "**GitHub Repository**: [anand-testcompare/dspy-reference-examples](https://github.com/anand-testcompare/dspy-reference-examples)\n"
        "**Learn More**: [shpit.dev/learn](https://shpit.dev/learn)"
    ),
    lifespan=_lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    request.state.request_id = request_id
    request.state.logger = logger.bind(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/", tags=["system"], summary="API Root")
def root() -> dict[str, str | dict[str, str]]:
    return {
        "name": "DSPy Complaint Classifier API",
        "version": "0.4.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "ae_pc": "/classify/ae-pc",
            "ae_category": "/classify/ae-category",
            "pc_category": "/classify/pc-category",
        },
    }


@app.get("/health", tags=["system"], summary="Health check")
def healthcheck() -> dict[str, str | dict]:
    errors = getattr(app.state, "errors", {})

    classifier_status = {
        ClassificationType.AE_PC: "ok" if getattr(app.state, "ae_pc_predictor", None) else "unavailable",
        ClassificationType.AE_CATEGORY: "ok" if getattr(app.state, "ae_category_predictor", None) else "unavailable",
        ClassificationType.PC_CATEGORY: "ok" if getattr(app.state, "pc_category_predictor", None) else "unavailable",
    }

    overall_status = "ok" if all(s == "ok" for s in classifier_status.values()) else "degraded"

    response = {
        "status": overall_status,
        "classifiers": classifier_status,
    }

    if errors:
        response["errors"] = errors

    return response


@app.post(
    "/classify/ae-pc",
    response_model=ComplaintResponse,
    summary="Classify as Adverse Event or Product Complaint",
    description=(
        "First-stage classification that determines whether a complaint is "
        "an Adverse Event (medical/health issue) or a Product Complaint (quality/defect issue)."
    ),
    tags=["classification"],
)
def classify_ae_pc(payload: AEPCRequest) -> ComplaintResponse:
    predictor = getattr(app.state, "ae_pc_predictor", None)
    if predictor is None:
        error_detail = app.state.errors.get(ClassificationType.AE_PC, "Classifier artifact not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AE-PC classifier unavailable: {error_detail}",
        )
    return predictor(payload)


@app.post(
    "/classify/ae-category",
    response_model=ComplaintResponse,
    summary="Classify Adverse Event into medical category",
    description=(
        "Second-stage classification for Adverse Events. Classifies into specific medical categories "
        "such as Gastrointestinal disorders, Pancreatitis, Hypoglycemia, etc."
    ),
    tags=["classification"],
)
def classify_ae_category(payload: AECategoryRequest) -> ComplaintResponse:
    predictor = getattr(app.state, "ae_category_predictor", None)
    if predictor is None:
        error_detail = app.state.errors.get(ClassificationType.AE_CATEGORY, "Classifier artifact not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AE-Category classifier unavailable: {error_detail}",
        )
    return predictor(payload)


@app.post(
    "/classify/pc-category",
    response_model=ComplaintResponse,
    summary="Classify Product Complaint into quality/defect category",
    description=(
        "Second-stage classification for Product Complaints. Classifies into specific categories "
        "such as Device malfunction, Storage/Temperature excursion, Packaging defect, etc."
    ),
    tags=["classification"],
)
def classify_pc_category(payload: PCCategoryRequest) -> ComplaintResponse:
    predictor = getattr(app.state, "pc_category_predictor", None)
    if predictor is None:
        error_detail = app.state.errors.get(ClassificationType.PC_CATEGORY, "Classifier artifact not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"PC-Category classifier unavailable: {error_detail}",
        )
    return predictor(payload)


__all__ = ["app"]
