"""Common filesystem paths used across the project."""

from __future__ import annotations

from pathlib import Path

from .types import ClassificationType

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"

CLASSIFICATION_TYPES: dict[ClassificationType, str] = {
    ClassificationType.AE_PC: "ae-pc-classification",
    ClassificationType.AE_CATEGORY: "ae-category-classification",
    ClassificationType.PC_CATEGORY: "pc-category-classification",
}

DEFAULT_CLASSIFICATION_TYPE = ClassificationType.AE_PC


def get_classification_data_dir(classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the data directory for a specific classification type."""
    if classification_type not in CLASSIFICATION_TYPES:
        raise ValueError(
            f"Invalid classification type: {classification_type}. "
            f"Valid types: {', '.join(t.value for t in ClassificationType)}"
        )
    return DATA_DIR / CLASSIFICATION_TYPES[classification_type]


def get_train_data_path(classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the training data path for a specific classification type."""
    return get_classification_data_dir(classification_type) / "train.json"


def get_test_data_path(classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the test data path for a specific classification type."""
    return get_classification_data_dir(classification_type) / "test.json"


def get_classifier_artifact_path(classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE) -> Path:
    """Get the artifact path for a specific classification type."""
    type_slug = CLASSIFICATION_TYPES[classification_type].replace("-classification", "")
    return ARTIFACTS_DIR / f"ozempic_classifier_{type_slug}_optimized.json"


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
]
