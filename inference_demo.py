"""Quick inference script using the optimized DSPy classifier via Pydantic models."""

from __future__ import annotations

import time

from src.common.config import configure_lm
from src.serving.service import ComplaintRequest, get_classification_function

configure_lm()

try:
    predict = get_classification_function()
except FileNotFoundError:
    raise SystemExit(
        "Optimized artifact missing. Run 'uv run python -m src.pipeline.main' before running this demo."
    ) from None

new_complaints = [
    {
        "id": 1,
        "text": "After my first Ozempic injection yesterday, I developed severe hives all over my body and my throat started swelling. Had to use my EpiPen.",
    },
    {
        "id": 2,
        "text": "The Ozempic pen I received has a crack in the barrel and is leaking medication. Haven't used it yet.",
    },
    {
        "id": 3,
        "text": "Been on Ozempic for 8 weeks. Yesterday I started having severe chest pain and shortness of breath. ER diagnosed acute myocardial infarction.",
    },
    {
        "id": 4,
        "text": "My pharmacy sent me Ozempic but the cold pack was completely warm and melted. Box felt room temperature.",
    },
    {
        "id": 5,
        "text": "I've had constant nausea and vomiting since starting Ozempic. Can't keep any food down for the past month. Lost 30 pounds.",
    },
]

print("=" * 70)
print("CLASSIFYING NEW COMPLAINTS")
print("=" * 70 + "\n")

total_time = 0.0

for complaint in new_complaints:
    request = ComplaintRequest(complaint=complaint["text"])
    print(
        f"Complaint #{complaint['id']}: {complaint['text'][:80]}..."
        if len(complaint["text"]) > 80
        else f"Complaint #{complaint['id']}: {complaint['text']}"
    )

    start = time.time()
    response = predict(request)
    elapsed = time.time() - start
    total_time += elapsed

    print(f"  Classification: {response.classification}")
    print(f"  Justification: {response.justification}")
    print(f"  Time: {elapsed:.3f}s\n")

avg_time = total_time / len(new_complaints)

print("=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
print(f"Total complaints: {len(new_complaints)}")
print(f"Total time: {total_time:.3f}s")
print(f"Average time per complaint: {avg_time:.3f}s")
print(f"Throughput: {1 / avg_time:.1f} complaints/second")
print("=" * 70)
