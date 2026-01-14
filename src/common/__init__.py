"""Shared DSPy classifier components."""

from .classifier import (
    CLASSIFICATION_CONFIGS,
    ClassificationConfig,
    ComplaintClassifier,
    classification_metric,
    create_classification_signature,
    evaluate_model,
)
from .config import (
    DEFAULT_CACHE_DIR,
    LLMConfig,
    configure_lm,
    ensure_dspy_cache_dir,
    load_llm_config,
)
from .data_utils import prepare_datasets
from .paths import (
    ARTIFACTS_DIR,
    CLASSIFICATION_TYPES,
    DATA_DIR,
    DEFAULT_CLASSIFICATION_TYPE,
    ROOT_DIR,
    get_classification_data_dir,
    get_classifier_artifact_path,
    get_test_data_path,
    get_train_data_path,
)
from .types import ClassificationType

__all__ = [
    "CLASSIFICATION_CONFIGS",
    "ClassificationConfig",
    "create_classification_signature",
    "ComplaintClassifier",
    "classification_metric",
    "evaluate_model",
    "configure_lm",
    "ensure_dspy_cache_dir",
    "DEFAULT_CACHE_DIR",
    "LLMConfig",
    "load_llm_config",
    "prepare_datasets",
    "ROOT_DIR",
    "DATA_DIR",
    "ARTIFACTS_DIR",
    "CLASSIFICATION_TYPES",
    "DEFAULT_CLASSIFICATION_TYPE",
    "ClassificationType",
    "get_classification_data_dir",
    "get_train_data_path",
    "get_test_data_path",
    "get_classifier_artifact_path",
]
