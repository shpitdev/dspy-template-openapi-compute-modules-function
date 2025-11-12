"""Shared DSPy classifier components."""

from .classifier import (
    CLASSIFICATION_CONFIGS,
    ComplaintClassifier,
    classification_metric,
    create_classification_signature,
    evaluate_model,
)
from .config import LLMConfig, configure_lm, load_llm_config
from .data_utils import prepare_datasets
from .paths import (
    ARTIFACTS_DIR,
    CLASSIFICATION_TYPES,
    DATA_DIR,
    DEFAULT_CLASSIFICATION_TYPE,
    DEFAULT_CLASSIFIER_PATH,
    ROOT_DIR,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
    get_classification_data_dir,
    get_classifier_artifact_path,
    get_test_data_path,
    get_train_data_path,
)

__all__ = [
    "CLASSIFICATION_CONFIGS",
    "create_classification_signature",
    "ComplaintClassifier",
    "classification_metric",
    "evaluate_model",
    "configure_lm",
    "LLMConfig",
    "load_llm_config",
    "prepare_datasets",
    "ROOT_DIR",
    "DATA_DIR",
    "ARTIFACTS_DIR",
    "CLASSIFICATION_TYPES",
    "DEFAULT_CLASSIFICATION_TYPE",
    "TRAIN_DATA_PATH",
    "TEST_DATA_PATH",
    "DEFAULT_CLASSIFIER_PATH",
    "get_classification_data_dir",
    "get_train_data_path",
    "get_test_data_path",
    "get_classifier_artifact_path",
]
