"""Entrypoint for training and optimizing the Ozempic DSPy classifier."""

from __future__ import annotations

import argparse
import json

from dspy.teleprompt import MIPROv2

from ..common.classifier import (
    CLASSIFICATION_CONFIGS,
    ComplaintClassifier,
    classification_metric,
    evaluate_model,
)
from ..common.config import configure_lm, get_display_model_name
from ..common.data_utils import prepare_datasets
from ..common.logging import configure_logging
from ..common.paths import (
    ARTIFACTS_DIR,
    CLASSIFICATION_TYPES,
    DEFAULT_CLASSIFICATION_TYPE,
    get_classifier_artifact_path,
)
from ..common.types import ClassificationType


def run_pipeline(classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE) -> None:
    """Train, optimize, and evaluate the classifier, then persist the artifact."""

    config = CLASSIFICATION_CONFIGS[classification_type]
    folder_name = CLASSIFICATION_TYPES[classification_type]

    print("\n" + "=" * 60)
    print("DSPy Ozempic Complaint Classifier")
    print(f"Classification Type: {folder_name}")
    print(f"Task: {config.description}")
    print("=" * 60 + "\n")

    configure_lm()

    print(f"Loading training and test data for {classification_type}...")
    trainset, testset = prepare_datasets(classification_type)
    print(f"✓ Loaded {len(trainset)} training examples")
    print(f"✓ Loaded {len(testset)} test examples\n")

    baseline_classifier = ComplaintClassifier(classification_type)

    print("\n" + "🔵 BASELINE PERFORMANCE (No Optimization)")
    baseline_accuracy = evaluate_model(baseline_classifier, testset, "Test Set")

    print("\n" + "🔄 OPTIMIZING WITH DSPy...")
    print("Using MIPROv2 optimizer")
    print("This may take a few minutes...\n")

    optimizer = MIPROv2(
        metric=classification_metric,
        auto="medium",
        verbose=True,
    )

    optimized_classifier = optimizer.compile(
        ComplaintClassifier(classification_type),
        trainset=trainset,
        max_bootstrapped_demos=3,
        max_labeled_demos=4,
    )

    print("✓ Optimization complete!\n")

    print("\n" + "🟢 OPTIMIZED PERFORMANCE")
    optimized_accuracy = evaluate_model(optimized_classifier, testset, "Test Set")

    print("\n" + "=" * 60)
    print("FINAL RESULTS SUMMARY")
    print("=" * 60)
    print(f"Baseline Accuracy:   {baseline_accuracy:.1%}")
    print(f"Optimized Accuracy:  {optimized_accuracy:.1%}")
    print(f"Improvement:         {optimized_accuracy - baseline_accuracy:+.1%}")
    print("=" * 60 + "\n")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = get_classifier_artifact_path(classification_type)

    print("Saving optimized model...")
    optimized_classifier.save(str(artifact_path))

    model_name = get_display_model_name()
    if model_name or classification_type:
        with open(artifact_path) as f:
            artifact_data = json.load(f)

        # Ensure metadata section exists
        if "metadata" not in artifact_data:
            artifact_data["metadata"] = {}

        # Add model and classification type information to metadata
        if model_name:
            print(f"Including model information: {model_name}")
            artifact_data["metadata"]["model"] = model_name

        artifact_data["metadata"]["classification_type"] = classification_type
        artifact_data["metadata"]["classification_config"] = config.model_dump()

        # Save the updated artifact
        with open(artifact_path, "w") as f:
            json.dump(artifact_data, f, indent=2)

    print(f"✓ Saved to: {artifact_path}\n")


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="Train and optimize the Ozempic complaint classifier")
    parser.add_argument(
        "--classification-type",
        "-t",
        type=str,
        default=DEFAULT_CLASSIFICATION_TYPE,
        choices=list(CLASSIFICATION_TYPES.keys()),
        help=f"Classification type to train (default: {DEFAULT_CLASSIFICATION_TYPE})",
    )

    args = parser.parse_args()
    run_pipeline(args.classification_type)


if __name__ == "__main__":
    main()
