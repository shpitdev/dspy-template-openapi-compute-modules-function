"""Common filesystem paths used across the project."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
TRAIN_DATA_PATH = DATA_DIR / "train.json"
TEST_DATA_PATH = DATA_DIR / "test.json"
DEFAULT_CLASSIFIER_PATH = ARTIFACTS_DIR / "ozempic_classifier_optimized.json"

__all__ = [
    "ROOT_DIR",
    "DATA_DIR",
    "ARTIFACTS_DIR",
    "TRAIN_DATA_PATH",
    "TEST_DATA_PATH",
    "DEFAULT_CLASSIFIER_PATH",
]
