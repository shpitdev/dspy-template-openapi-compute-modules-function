"""Core DSPy classifier definitions and helpers."""

from __future__ import annotations

import dspy
from pydantic import BaseModel

from .types import ClassificationType


class ClassificationConfig(BaseModel):
    """Configuration for a single classification type."""

    description: str
    labels: list[str]

    @property
    def output_desc(self) -> str:
        return f"One of: {', '.join(self.labels)}"


CLASSIFICATION_CONFIGS: dict[ClassificationType, ClassificationConfig] = {
    ClassificationType.AE_PC: ClassificationConfig(
        description="Classify Ozempic-related complaints as Adverse Event or Product Complaint.",
        labels=["Adverse Event", "Product Complaint"],
    ),
    ClassificationType.AE_CATEGORY: ClassificationConfig(
        description="Classify adverse events into specific categories.",
        labels=[
            "Gastrointestinal disorders",
            "Pancreatitis",
            "Hepatobiliary (gallbladder) disease",
            "Hypoglycemia",
            "Eye disorders (Diabetic retinopathy complications)",
            "Renal events (Acute kidney injury)",
            "Hypersensitivity",
            "Injection-site reactions",
            "Cardiovascular signs",
            "Peri-procedural aspiration risk",
            "Gastrointestinal disorders (Gastroparesis)",
        ],
    ),
    ClassificationType.PC_CATEGORY: ClassificationConfig(
        description="Classify product complaints into specific categories.",
        labels=[
            "Stability/Appearance defect",
            "Device malfunction",
            "Storage/Temperature excursion",
            "Labeling error",
            "Contamination/Foreign matter",
            "Packaging defect",
            "Counterfeit/Unauthorized source",
            "Potency/Assay defect",
            "Distribution/Expiry",
        ],
    ),
}


def create_classification_signature(
    classification_type: ClassificationType = ClassificationType.AE_PC,
) -> type[dspy.Signature]:
    """Create a classification signature dynamically based on the classification type."""
    if classification_type not in CLASSIFICATION_CONFIGS:
        raise ValueError(
            f"Invalid classification type: {classification_type}. "
            f"Valid types: {', '.join(t.value for t in ClassificationType)}"
        )
    config = CLASSIFICATION_CONFIGS[classification_type]

    class ComplaintClassification(dspy.Signature):
        __doc__ = config.description
        complaint = dspy.InputField(desc="The complaint text about Ozempic")
        classification = dspy.OutputField(desc=config.output_desc)
        justification = dspy.OutputField(desc="Brief explanation for the classification")

    return ComplaintClassification


class ComplaintClassifier(dspy.Module):
    """DSPy module wrapping the complaint classification prompt."""

    def __init__(self, classification_type: ClassificationType = ClassificationType.AE_PC):
        super().__init__()
        self.classification_type = classification_type
        signature = create_classification_signature(classification_type)
        self.classify = dspy.ChainOfThought(signature)

    def forward(self, complaint: str) -> dspy.Prediction:
        result = self.classify(complaint=complaint)
        return dspy.Prediction(
            classification=result.classification,
            justification=result.justification,
        )


def classification_metric(example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
    """Return 1.0 if the predicted label matches the ground truth."""

    if pred.classification is None:
        return 0.0
    predicted = pred.classification.strip().lower()
    actual = example.classification.strip().lower()
    return float(predicted == actual)


def evaluate_model(
    model: ComplaintClassifier,
    dataset: list[dspy.Example],
    dataset_name: str,
    verbose: bool = False,
) -> float:
    correct = 0
    total = len(dataset)

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Evaluating on {dataset_name} ({total} examples)")
        print(f"{'=' * 60}\n")

    for i, example in enumerate(dataset, start=1):
        prediction = model(complaint=example.complaint)
        is_correct = classification_metric(example, prediction)
        correct += is_correct

        if verbose:
            status = "✓" if is_correct else "✗"
            print(f"{status} Example {i}/{total}")
            print(f"  Complaint: {example.complaint[:80]}...")
            print(f"  Predicted: {prediction.classification or '(None - truncated response)'}")
            print(f"  Actual: {example.classification}")
            if not is_correct:
                print(f"  Justification: {prediction.justification or '(None)'}")
            print()

    accuracy = correct / total

    if verbose:
        print(f"{'=' * 60}")
        print(f"Accuracy: {correct}/{total} = {accuracy:.1%}")
        print(f"{'=' * 60}\n")

    return accuracy


__all__ = [
    "ClassificationConfig",
    "CLASSIFICATION_CONFIGS",
    "create_classification_signature",
    "ComplaintClassifier",
    "classification_metric",
    "evaluate_model",
]
