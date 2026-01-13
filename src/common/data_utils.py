"""Utilities for loading Ozempic complaint datasets."""

from __future__ import annotations

import json
from pathlib import Path

import dspy

from .paths import (
    DEFAULT_CLASSIFICATION_TYPE,
    get_test_data_path,
    get_train_data_path,
)
from .types import ClassificationType


def _load_split(path: Path, classification_type: ClassificationType) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file '{path}' is missing for classification type '{classification_type}'. "
            f"Run the appropriate data generation script first."
        )

    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def prepare_datasets(
    classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE,
) -> tuple[list[dspy.Example], list[dspy.Example]]:
    """Load training/test datasets and convert them into DSPy Examples."""

    train_path = get_train_data_path(classification_type)
    test_path = get_test_data_path(classification_type)

    train_raw = _load_split(train_path, classification_type)
    test_raw = _load_split(test_path, classification_type)

    def _to_examples(raw_batch: list[dict]) -> list[dspy.Example]:
        # Handle both "label" and "category" keys for backwards compatibility
        return [
            dspy.Example(
                complaint=item.get("complaint") or item.get("narrative", ""),
                classification=item.get("label") or item.get("category", ""),
            ).with_inputs("complaint")
            for item in raw_batch
        ]

    return _to_examples(train_raw), _to_examples(test_raw)


__all__ = ["prepare_datasets"]
