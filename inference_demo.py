"""
Quick inference script using the optimized DSPy classifier.
Demonstrates real-world usage and speed for classifying new complaints.
"""

import os
import time
from dotenv import load_dotenv
import dspy

# Load environment variables
load_dotenv()

# Configure DSPy
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    exit(1)

lm = dspy.LM('openai/gpt-4o-mini', api_key=api_key)
dspy.configure(lm=lm)

# Load the optimized classifier
print("Loading optimized classifier...")
from ozempic_classifier import ComplaintClassifier
classifier = ComplaintClassifier()
classifier.load("ozempic_classifier_optimized.json")
print("✓ Loaded optimized model\n")

# New example complaints to classify
new_complaints = [
    {
        "id": 1,
        "text": "After my first Ozempic injection yesterday, I developed severe hives all over my body and my throat started swelling. Had to use my EpiPen."
    },
    {
        "id": 2,
        "text": "The Ozempic pen I received has a crack in the barrel and is leaking medication. Haven't used it yet."
    },
    {
        "id": 3,
        "text": "Been on Ozempic for 8 weeks. Yesterday I started having severe chest pain and shortness of breath. ER diagnosed acute myocardial infarction."
    },
    {
        "id": 4,
        "text": "My pharmacy sent me Ozempic but the cold pack was completely warm and melted. Box felt room temperature."
    },
    {
        "id": 5,
        "text": "I've had constant nausea and vomiting since starting Ozempic. Can't keep any food down for the past month. Lost 30 pounds."
    }
]

print("=" * 70)
print("CLASSIFYING NEW COMPLAINTS")
print("=" * 70 + "\n")

total_time = 0

for complaint in new_complaints:
    print(f"Complaint #{complaint['id']}:")
    print(f"Text: {complaint['text'][:80]}..." if len(complaint['text']) > 80 else f"Text: {complaint['text']}")

    # Time the classification
    start_time = time.time()
    result = classifier(complaint=complaint['text'])
    end_time = time.time()

    elapsed = end_time - start_time
    total_time += elapsed

    print(f"Classification: {result.classification}")
    print(f"Justification: {result.justification}")
    print(f"Time: {elapsed:.3f}s")
    print()

avg_time = total_time / len(new_complaints)

print("=" * 70)
print(f"PERFORMANCE SUMMARY")
print("=" * 70)
print(f"Total complaints: {len(new_complaints)}")
print(f"Total time: {total_time:.3f}s")
print(f"Average time per complaint: {avg_time:.3f}s")
print(f"Throughput: {1/avg_time:.1f} complaints/second")
print("=" * 70)
