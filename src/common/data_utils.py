"""Utilities for loading Ozempic complaint datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import dspy

from .paths import TRAIN_DATA_PATH, TEST_DATA_PATH


def _load_split(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file '{path}' is missing. Run 'python scripts/generate_sample_data_ozempic_pc_vs_ae.py' first."
        )

    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def prepare_datasets() -> Tuple[list[dspy.Example], list[dspy.Example]]:
    """Load training/test datasets and convert them into DSPy Examples."""

    train_raw = _load_split(TRAIN_DATA_PATH)
    test_raw = _load_split(TEST_DATA_PATH)

    def _to_examples(raw_batch: List[dict]) -> list[dspy.Example]:
        return [
            dspy.Example(
                complaint=item["complaint"],
                classification=item["label"],
            ).with_inputs("complaint")
            for item in raw_batch
        ]

    return _to_examples(train_raw), _to_examples(test_raw)


__all__ = ["prepare_datasets"]
