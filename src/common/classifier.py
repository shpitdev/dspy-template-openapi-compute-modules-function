"""Core DSPy classifier definitions and helpers."""

from __future__ import annotations

import dspy


class ComplaintClassification(dspy.Signature):
    """Classify Ozempic-related complaints as Adverse Event or Product Complaint."""

    complaint = dspy.InputField(desc="The complaint text about Ozempic")
    classification = dspy.OutputField(desc="Either 'Adverse Event' or 'Product Complaint'")
    justification = dspy.OutputField(desc="Brief explanation for the classification")


class ComplaintClassifier(dspy.Module):
    """DSPy module wrapping the complaint classification prompt."""

    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(ComplaintClassification)

    def forward(self, complaint: str) -> dspy.Prediction:
        result = self.classify(complaint=complaint)
        return dspy.Prediction(
            classification=result.classification,
            justification=result.justification,
        )


def classification_metric(example: dspy.Example, pred: dspy.Prediction, trace=None) -> float:
    """Return 1.0 if the predicted label matches the ground truth."""

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
        print(f"  Predicted: {prediction.classification}")
        print(f"  Actual: {example.classification}")
        if not is_correct:
            print(f"  Justification: {prediction.justification}")
        print()

    accuracy = correct / total
    print(f"{'=' * 60}")
    print(f"Accuracy: {correct}/{total} = {accuracy:.1%}")
    print(f"{'=' * 60}\n")

    return accuracy


__all__ = [
    "ComplaintClassification",
    "ComplaintClassifier",
    "classification_metric",
    "evaluate_model",
]
