"""
DocuLens Automated RAG Evaluation Script using Ragas
Evaluates the RAG Triad:
1. Faithfulness (Zero Hallucination)
2. Answer Relevance
3. Context Precision & Recall
"""

import json
from typing import List, Dict, Any
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

def run_rag_eval(evaluation_samples: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Input format:
    [
        {
            "question": "What was the total capital expenditure in FY2023?",
            "answer": "In FY2023, capital expenditures were $12.4 billion [Doc: 10K.pdf, Page: 42].",
            "contexts": ["Capital expenditures for the year ended December 31, 2023 were $12,410 million..."],
            "ground_truth": "Capital expenditures were $12.4 billion for fiscal year 2023."
        }
    ]
    """
    # Convert samples to Hugging Face Dataset format required by Ragas
    data = {
        "question": [s["question"] for s in evaluation_samples],
        "answer": [s["answer"] for s in evaluation_samples],
        "contexts": [s["contexts"] for s in evaluation_samples],
        "ground_truth": [s["ground_truth"] for s in evaluation_samples],
    }
    dataset = Dataset.from_dict(data)

    # Execute evaluation pipeline
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    score_dict = {
        "faithfulness": float(results["faithfulness"]),
        "answer_relevancy": float(results["answer_relevancy"]),
        "context_precision": float(results["context_precision"]),
        "context_recall": float(results["context_recall"]),
    }

    print("\n================ RAGAS BENCHMARK RESULTS ================")
    for metric, score in score_dict.items():
        print(f"  {metric:20s}: {score:.4f}")
    print("========================================================\n")

    return score_dict

if __name__ == "__main__":
    # Smoke test sample
    samples = [
        {
            "question": "What is the net revenue for Q4 2023?",
            "answer": "Net revenue for Q4 2023 was $18.5 billion [Doc: Q4_Report.pdf, Page: 12].",
            "contexts": ["During the fourth quarter of 2023, consolidated net revenues reached $18,520 million."],
            "ground_truth": "Net revenue was $18.5 billion for Q4 2023."
        }
    ]
    print("Running sample evaluation...")
    # results = run_rag_eval(samples)
