"""Core DSPy Ozempic classifier package."""

from .common import (
    ComplaintClassification,
    ComplaintClassifier,
    classification_metric,
    configure_lm,
    evaluate_model,
    prepare_datasets,
)
from .serving.service import (
    ComplaintRequest,
    ComplaintResponse,
    get_classification_function,
)

__all__ = [
    "ComplaintClassifier",
    "ComplaintClassification",
    "classification_metric",
    "configure_lm",
    "evaluate_model",
    "prepare_datasets",
    "ComplaintRequest",
    "ComplaintResponse",
    "get_classification_function",
]
