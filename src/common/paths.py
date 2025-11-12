"""Common filesystem paths used across the project."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"

# Classification types
CLASSIFICATION_TYPES = {
    "ae-pc": "ae-pc-classification",
    "ae-category": "ae-category-classification",
    "pc-category": "pc-category-classification",
}

# Default classification type
DEFAULT_CLASSIFICATION_TYPE = "ae-pc"


def get_classification_data_dir(classification_type: str = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the data directory for a specific classification type."""
    if classification_type not in CLASSIFICATION_TYPES:
        raise ValueError(
            f"Invalid classification type: {classification_type}. Valid types: {', '.join(CLASSIFICATION_TYPES.keys())}"
        )
    return DATA_DIR / CLASSIFICATION_TYPES[classification_type]


def get_train_data_path(classification_type: str = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the training data path for a specific classification type."""
    return get_classification_data_dir(classification_type) / "train.json"


def get_test_data_path(classification_type: str = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the test data path for a specific classification type."""
    return get_classification_data_dir(classification_type) / "test.json"


def get_classifier_artifact_path(classification_type: str = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the artifact path for a specific classification type."""
    type_slug = CLASSIFICATION_TYPES[classification_type].replace("-classification", "")
    return ARTIFACTS_DIR / f"ozempic_classifier_{type_slug}_optimized.json"


# Backwards compatibility - keep old constants using default type
TRAIN_DATA_PATH = get_train_data_path()
TEST_DATA_PATH = get_test_data_path()
DEFAULT_CLASSIFIER_PATH = get_classifier_artifact_path()

__all__ = [
    "ROOT_DIR",
    "DATA_DIR",
    "ARTIFACTS_DIR",
    "CLASSIFICATION_TYPES",
    "DEFAULT_CLASSIFICATION_TYPE",
    "get_classification_data_dir",
    "get_train_data_path",
    "get_test_data_path",
    "get_classifier_artifact_path",
    "TRAIN_DATA_PATH",
    "TEST_DATA_PATH",
    "DEFAULT_CLASSIFIER_PATH",
]
