"""Service helpers that expose the classifier through Pydantic models."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

import dspy
from pydantic import BaseModel, ConfigDict, Field

from ..common.classifier import CLASSIFICATION_CONFIGS, ComplaintClassifier
from ..common.config import get_display_model_name
from ..common.paths import get_classifier_artifact_path
from ..common.types import ClassificationType


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


def _update_artifact_model_metadata(model_path: Path, current_model: str) -> None:
    try:
        artifact_data = json.loads(model_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    metadata = artifact_data.get("metadata")
    saved_model = metadata.get("model") if isinstance(metadata, dict) else None
    if saved_model == current_model:
        return

    if not isinstance(metadata, dict):
        metadata = {}
        artifact_data["metadata"] = metadata
    metadata["model"] = current_model

    tmp_path = model_path.with_suffix(f"{model_path.suffix}.tmp")
    try:
        tmp_path.write_text(json.dumps(artifact_data, indent=2) + "\n", encoding="utf-8")
        tmp_path.replace(model_path)
    except OSError:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _artifact_auto_update_enabled() -> bool:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return False
    flag = os.getenv("DSPY_ARTIFACT_AUTO_UPDATE", "").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def _load_classifier(model_path: Path, classification_type: ClassificationType) -> ComplaintClassifier:
    """Load a classifier for a specific classification type."""
    classifier = ComplaintClassifier(classification_type)
    classifier.load(str(model_path))
    current_model = get_display_model_name()
    if current_model and _artifact_auto_update_enabled():
        _update_artifact_model_metadata(model_path, current_model)
    return classifier


@lru_cache(maxsize=3)
def _cached_classifier(model_path: Path, classification_type: ClassificationType) -> ComplaintClassifier:
    """Cache classifiers by both path and classification type."""
    return _load_classifier(model_path, classification_type)


def _create_classification_function(
    classification_type: ClassificationType,
    use_cache: bool = True,
) -> Callable[[ComplaintRequest], ComplaintResponse]:
    """Create a classification function for a specific classification type."""
    if classification_type not in CLASSIFICATION_CONFIGS:
        raise ValueError(
            f"Invalid classification type: {classification_type}. "
            f"Valid types: {', '.join(t.value for t in ClassificationType)}"
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
    return _create_classification_function(ClassificationType.AE_PC, use_cache)


def get_ae_category_classifier(use_cache: bool = True) -> Callable[[AECategoryRequest], ComplaintResponse]:
    """Get classifier for Adverse Event category classification."""
    return _create_classification_function(ClassificationType.AE_CATEGORY, use_cache)


def get_pc_category_classifier(use_cache: bool = True) -> Callable[[PCCategoryRequest], ComplaintResponse]:
    """Get classifier for Product Complaint category classification."""
    return _create_classification_function(ClassificationType.PC_CATEGORY, use_cache)


def get_classification_function(
    classification_type: ClassificationType = ClassificationType.AE_PC,
    use_cache: bool = True,
) -> Callable[[ComplaintRequest], ComplaintResponse]:
    """Get a classification function for the requested classification type."""
    return _create_classification_function(classification_type, use_cache)


__all__ = [
    "ComplaintRequest",
    "AEPCRequest",
    "AECategoryRequest",
    "PCCategoryRequest",
    "ComplaintResponse",
    "get_ae_pc_classifier",
    "get_ae_category_classifier",
    "get_pc_category_classifier",
    "get_classification_function",
]
