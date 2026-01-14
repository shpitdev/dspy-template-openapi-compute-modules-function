"""Entrypoint for training and optimizing the Ozempic DSPy classifier."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from pathlib import Path

import dspy
from dspy.teleprompt import MIPROv2

import mlflow

from ..common.classifier import (
    CLASSIFICATION_CONFIGS,
    ComplaintClassifier,
    classification_metric,
    evaluate_model,
)
from ..common.config import configure_lm, get_display_model_name
from ..common.data_utils import prepare_datasets
from ..common.paths import (
    ARTIFACTS_DIR,
    CLASSIFICATION_TYPES,
    DEFAULT_CLASSIFICATION_TYPE,
    get_classifier_artifact_path,
)
from ..common.types import ClassificationType

# MLflow configuration - SQLite backend for easy querying
MLFLOW_DB_PATH = Path("mlflow/mlflow.db")
MLFLOW_ARTIFACTS_PATH = Path("mlflow/artifacts")


def setup_mlflow() -> None:
    """Configure MLflow with SQLite backend."""
    MLFLOW_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    MLFLOW_ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)

    # Set tracking URI to SQLite database
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB_PATH}")

    # Set artifact location
    os.environ["MLFLOW_ARTIFACT_ROOT"] = str(MLFLOW_ARTIFACTS_PATH.absolute())


def run_pipeline(
    classification_type: ClassificationType = DEFAULT_CLASSIFICATION_TYPE,
    verbose: bool = False,
) -> None:
    config = CLASSIFICATION_CONFIGS[classification_type]
    folder_name = CLASSIFICATION_TYPES[classification_type]
    model_name = get_display_model_name()
    run_id = os.getenv("DSPY_RUN_ID") or uuid.uuid4().hex[:8]

    print(f"\nTraining {folder_name} classifier (run: {run_id})...")

    setup_mlflow()
    mlflow.set_experiment(f"dspy-classifier-{folder_name}")
    configure_lm()

    trainset, testset = prepare_datasets(classification_type)
    print(f"  Data: {len(trainset)} train, {len(testset)} test")

    with mlflow.start_run(run_name=f"{folder_name}-{run_id}"):
        mlflow.log_params(
            {
                "classification_type": classification_type,
                "model": model_name or "unknown",
                "train_size": len(trainset),
                "test_size": len(testset),
                "optimizer": "MIPROv2",
                "optimizer_auto": "medium",
                "max_bootstrapped_demos": 3,
                "max_labeled_demos": 4,
            }
        )
        mlflow.log_dict(config.model_dump(), "classification_config.json")

        baseline_classifier = ComplaintClassifier(classification_type)
        print("  Evaluating baseline...")
        baseline_accuracy = evaluate_model(baseline_classifier, testset, "Test Set", verbose=verbose)
        mlflow.log_metric("baseline_accuracy", baseline_accuracy)

        print("  Optimizing with MIPROv2...")
        optimizer = MIPROv2(
            metric=classification_metric,
            auto="medium",
            verbose=verbose,
        )
        optimized_classifier = optimizer.compile(
            ComplaintClassifier(classification_type),
            trainset=trainset,
            max_bootstrapped_demos=3,
            max_labeled_demos=4,
        )

        print("  Evaluating optimized...")
        optimized_accuracy = evaluate_model(optimized_classifier, testset, "Test Set", verbose=verbose)
        mlflow.log_metric("optimized_accuracy", optimized_accuracy)

        improvement = optimized_accuracy - baseline_accuracy
        mlflow.log_metric("improvement", improvement)

        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        artifact_path = get_classifier_artifact_path(classification_type)
        optimized_classifier.save(str(artifact_path))

        if model_name or classification_type:
            with open(artifact_path) as f:
                artifact_data = json.load(f)
            if "metadata" not in artifact_data:
                artifact_data["metadata"] = {}
            if model_name:
                artifact_data["metadata"]["model"] = model_name
            artifact_data["metadata"]["classification_type"] = classification_type
            artifact_data["metadata"]["classification_config"] = config.model_dump()
            artifact_data["metadata"]["mlflow_run_id"] = run_id
            with open(artifact_path, "w") as f:
                json.dump(artifact_data, f, indent=2)

        mlflow.log_artifact(str(artifact_path))

        print(f"\nResults: {baseline_accuracy:.1%} → {optimized_accuracy:.1%} ({improvement:+.1%})")
        print(f"Artifact: {artifact_path}")
        active_run = mlflow.active_run()
        if active_run:
            print(f"MLflow: sqlite:///{MLFLOW_DB_PATH} (run: {active_run.info.run_id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and optimize the Ozempic complaint classifier")
    parser.add_argument(
        "--classification-type",
        "-t",
        type=str,
        default=DEFAULT_CLASSIFICATION_TYPE,
        choices=list(CLASSIFICATION_TYPES.keys()),
        help=f"Classification type to train (default: {DEFAULT_CLASSIFICATION_TYPE})",
    )
    parser.add_argument(
        "--inspect",
        "-i",
        action="store_true",
        help="Show DSPy prompt/response history after optimization (useful for demos)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (evaluation details, MIPROv2 progress)",
    )

    args = parser.parse_args()
    run_pipeline(args.classification_type, verbose=args.verbose)

    if args.inspect:
        print("\n" + "=" * 60)
        print("DSPy PROMPT/RESPONSE HISTORY")
        print("=" * 60)
        dspy.inspect_history(n=3)


if __name__ == "__main__":
    main()
