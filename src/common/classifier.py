"""Core DSPy classifier definitions and helpers."""

from __future__ import annotations

import dspy

# Classification type configurations
CLASSIFICATION_CONFIGS = {
    "ae-pc": {
        "description": "Classify Ozempic-related complaints as Adverse Event or Product Complaint.",
        "output_desc": "Either 'Adverse Event' or 'Product Complaint'",
        "labels": ["Adverse Event", "Product Complaint"],
    },
    "ae-category": {
        "description": "Classify adverse events into specific categories.",
        "output_desc": (
            "One of: Gastrointestinal disorders, Pancreatitis, "
            "Hepatobiliary (gallbladder) disease, Hypoglycemia, Eye disorders (Diabetic retinopathy complications), "
            "Renal events (Acute kidney injury), Hypersensitivity, Injection-site reactions, "
            "Cardiovascular signs, Peri-procedural aspiration risk, Gastrointestinal disorders (Gastroparesis)"
        ),
        "labels": [
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
    },
    "pc-category": {
        "description": "Classify product complaints into specific categories.",
        "output_desc": (
            "One of: Stability/Appearance defect, Device malfunction, Storage/Temperature excursion, "
            "Labeling error, Contamination/Foreign matter, Packaging defect, Counterfeit/Unauthorized source, "
            "Potency/Assay defect, Distribution/Expiry"
        ),
        "labels": [
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
    },
}


def create_classification_signature(classification_type: str = "ae-pc") -> type[dspy.Signature]:
    """Create a classification signature dynamically based on the classification type."""
    config = CLASSIFICATION_CONFIGS.get(classification_type)
    if not config:
        raise ValueError(
            f"Invalid classification type: {classification_type}. "
            f"Valid types: {', '.join(CLASSIFICATION_CONFIGS.keys())}"
        )

    class ComplaintClassification(dspy.Signature):
        __doc__ = config["description"]
        complaint = dspy.InputField(desc="The complaint text about Ozempic")
        classification = dspy.OutputField(desc=config["output_desc"])
        justification = dspy.OutputField(desc="Brief explanation for the classification")

    return ComplaintClassification


class ComplaintClassifier(dspy.Module):
    """DSPy module wrapping the complaint classification prompt."""

    def __init__(self, classification_type: str = "ae-pc"):
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


def evaluate_model(model: ComplaintClassifier, dataset: list[dspy.Example], dataset_name: str) -> float:
    """Evaluate a classifier on a dataset and log basic stats."""

    correct = 0
    total = len(dataset)

    print(f"\n{'=' * 60}")
    print(f"Evaluating on {dataset_name} ({total} examples)")
    print(f"{'=' * 60}\n")

    for i, example in enumerate(dataset, start=1):
        prediction = model(complaint=example.complaint)
        is_correct = classification_metric(example, prediction)
        correct += is_correct

        status = "✓" if is_correct else "✗"
        print(f"{status} Example {i}/{total}")
        print(f"  Complaint: {example.complaint[:80]}...")
        print(f"  Predicted: {prediction.classification or '(None - truncated response)'}")
        print(f"  Actual: {example.classification}")
        if not is_correct:
            print(f"  Justification: {prediction.justification or '(None)'}")
        print()

    accuracy = correct / total
    print(f"{'=' * 60}")
    print(f"Accuracy: {correct}/{total} = {accuracy:.1%}")
    print(f"{'=' * 60}\n")

    return accuracy


__all__ = [
    "CLASSIFICATION_CONFIGS",
    "create_classification_signature",
    "ComplaintClassifier",
    "classification_metric",
    "evaluate_model",
]
