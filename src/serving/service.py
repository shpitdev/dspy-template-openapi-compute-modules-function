"""Service helpers that expose the classifier through Pydantic models."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional

import dspy
from pydantic import BaseModel, ConfigDict, Field

from ..common.classifier import ComplaintClassifier
from ..common.paths import DEFAULT_CLASSIFIER_PATH


class ComplaintRequest(BaseModel):
    """Inbound payload for running a classification."""

    complaint: str = Field(..., description="Raw complaint text")
    model_path: Optional[str] = Field(
        default=None,
        description="Optional override for the optimized model artifact",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "complaint": "My Ozempic pen arrived with a cracked cartridge and leaked everywhere.",
                "model_path": None,
            }
        }
    )


class ComplaintResponse(BaseModel):
    """Structured prediction response."""

    classification: str
    justification: str


def _load_classifier(model_path: Path) -> ComplaintClassifier:
    classifier = ComplaintClassifier()
    classifier.load(str(model_path))
    return classifier


@lru_cache(maxsize=1)
def _cached_classifier(model_path: Path) -> ComplaintClassifier:
    return _load_classifier(model_path)


def get_classification_function(
    model_path: Optional[Path] = None,
    use_cache: bool = True,
) -> Callable[[ComplaintRequest], ComplaintResponse]:
    """Return a callable that takes a ComplaintRequest and returns a ComplaintResponse."""

    resolved_path = (model_path or DEFAULT_CLASSIFIER_PATH).expanduser().resolve()
    if use_cache:
        classifier = _cached_classifier(resolved_path)
    else:
        classifier = _load_classifier(resolved_path)

    def _predict(request: ComplaintRequest) -> ComplaintResponse:
        target_path = Path(request.model_path).expanduser().resolve() if request.model_path else resolved_path

        if target_path == resolved_path:
            active_classifier = classifier
        elif use_cache:
            active_classifier = _cached_classifier(target_path)
        else:
            active_classifier = _load_classifier(target_path)

        prediction: dspy.Prediction = active_classifier(complaint=request.complaint)
        return ComplaintResponse(
            classification=prediction.classification,
            justification=prediction.justification,
        )

    return _predict


__all__ = [
    "ComplaintRequest",
    "ComplaintResponse",
    "get_classification_function",
]
