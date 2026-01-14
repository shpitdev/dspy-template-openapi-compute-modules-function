"""Core DSPy Ozempic classifier package."""

from .common import (
    CLASSIFICATION_CONFIGS,
    ClassificationConfig,
    ComplaintClassifier,
    classification_metric,
    configure_lm,
    create_classification_signature,
    evaluate_model,
    prepare_datasets,
)
from .serving.service import (
    AECategoryRequest,
    AEPCRequest,
    ComplaintRequest,
    ComplaintResponse,
    PCCategoryRequest,
    get_ae_category_classifier,
    get_ae_pc_classifier,
    get_classification_function,
    get_pc_category_classifier,
)

__all__ = [
    "CLASSIFICATION_CONFIGS",
    "ClassificationConfig",
    "create_classification_signature",
    "ComplaintClassifier",
    "classification_metric",
    "configure_lm",
    "evaluate_model",
    "prepare_datasets",
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
