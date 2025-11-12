"""Service helpers that expose the classifier through Pydantic models."""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

import dspy
from pydantic import BaseModel, ConfigDict, Field

from ..common.classifier import CLASSIFICATION_CONFIGS, ComplaintClassifier
from ..common.paths import get_classifier_artifact_path


class ComplaintRequest(BaseModel):
    """Inbound payload for running a classification."""

    complaint: str = Field(..., description="Raw complaint text")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "complaint": "My Ozempic pen arrived with a cracked cartridge and leaked everywhere.",
            }
        }
    )


class AEPCRequest(ComplaintRequest):
    """Request for classifying as Adverse Event or Product Complaint."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "complaint": "I experienced severe nausea and vomiting after taking Ozempic.",
            }
        }
    )


class AECategoryRequest(ComplaintRequest):
    """Request for classifying Adverse Event into a specific category."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "complaint": "I developed pancreatitis after using Ozempic for 3 months.",
            }
        }
    )


class PCCategoryRequest(ComplaintRequest):
    """Request for classifying Product Complaint into a specific category."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "complaint": "The medication arrived warm, temperature control was not maintained during shipping.",
            }
        }
    )


class ComplaintResponse(BaseModel):
    """Structured prediction response."""

    classification: str
    justification: str
    classification_type: str = Field(..., description="The type of classification performed")


def _load_classifier(model_path: Path, classification_type: str) -> ComplaintClassifier:
    """Load a classifier for a specific classification type."""
    classifier = ComplaintClassifier(classification_type)
    classifier.load(str(model_path))
    return classifier


@lru_cache(maxsize=3)
def _cached_classifier(model_path: Path, classification_type: str) -> ComplaintClassifier:
    """Cache classifiers by both path and classification type."""
    return _load_classifier(model_path, classification_type)


def _create_classification_function(
    classification_type: str,
    use_cache: bool = True,
) -> Callable[[ComplaintRequest], ComplaintResponse]:
    """Create a classification function for a specific classification type."""

    # Validate classification type
    if classification_type not in CLASSIFICATION_CONFIGS:
        raise ValueError(
            f"Invalid classification type: {classification_type}. "
            f"Valid types: {', '.join(CLASSIFICATION_CONFIGS.keys())}"
        )

    model_path = get_classifier_artifact_path(classification_type)
    resolved_path = model_path.expanduser().resolve()

    if use_cache:
        classifier = _cached_classifier(resolved_path, classification_type)
    else:
        classifier = _load_classifier(resolved_path, classification_type)

    def _predict(request: ComplaintRequest) -> ComplaintResponse:
        prediction: dspy.Prediction = classifier(complaint=request.complaint)
        return ComplaintResponse(
            classification=prediction.classification,
            justification=prediction.justification,
            classification_type=classification_type,
        )

    return _predict


def get_ae_pc_classifier(use_cache: bool = True) -> Callable[[AEPCRequest], ComplaintResponse]:
    """Get classifier for Adverse Event vs Product Complaint classification."""
    return _create_classification_function("ae-pc", use_cache)


def get_ae_category_classifier(use_cache: bool = True) -> Callable[[AECategoryRequest], ComplaintResponse]:
    """Get classifier for Adverse Event category classification."""
    return _create_classification_function("ae-category", use_cache)


def get_pc_category_classifier(use_cache: bool = True) -> Callable[[PCCategoryRequest], ComplaintResponse]:
    """Get classifier for Product Complaint category classification."""
    return _create_classification_function("pc-category", use_cache)


__all__ = [
    "ComplaintRequest",
    "AEPCRequest",
    "AECategoryRequest",
    "PCCategoryRequest",
    "ComplaintResponse",
    "get_ae_pc_classifier",
    "get_ae_category_classifier",
    "get_pc_category_classifier",
]
