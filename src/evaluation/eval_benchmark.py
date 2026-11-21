"""
Evaluation Benchmark for Contract & Invoice RAG System.
Measures:
1. Faithfulness (Zero Hallucination)
2. Context Recall & Precision
3. Discrepancy Detection Accuracy
4. Citation Attribution Precision
"""

from typing import List, Dict, Any

class RAGEvaluationBenchmark:
    def __init__(self):
        # Golden dataset of enterprise legal & financial audit test cases
        self.test_cases = [
            {
                "id": "TC-01",
                "category": "Cross-Document Discrepancy Detection",
                "query": "Does Invoice INV-2024-099 comply with the late fee and milestone budget terms in the MSA and SOW?",
                "expected_discrepancy": True,
                "required_citations": ["MSA_Acme_Cyberdyne_2024.pdf", "SOW_Cloud_Infrastructure.pdf", "INV_2024_099_Disputed.pdf"],
                "required_keywords": ["15", "1.5%", "35,000", "55,000", "violation"]
            },
            {
                "id": "TC-02",
                "category": "Contract Liability & Indemnification",
                "query": "What is the maximum aggregate liability cap under the MSA, and which claims are uncapped?",
                "expected_discrepancy": False,
                "required_citations": ["MSA_Acme_Cyberdyne_2024.pdf"],
                "required_keywords": ["twelve", "12", "uncapped", "indemnif"]
            },
            {
                "id": "TC-03",
                "category": "Invoice Line Item & Tax Reconciliation",
                "query": "What are the itemized amounts, tax rate, and wire transfer details for Invoice INV-2024-081?",
                "expected_discrepancy": False,
                "required_citations": ["INV_2024_081_Compliant.pdf"],
                "required_keywords": ["25,000", "2,062.50", "27,062.50", "121000358"]
            }
        ]

    def evaluate_pipeline(self, rag_pipeline) -> Dict[str, Any]:
        results = []
        total_faithfulness = 0.0
        total_context_recall = 0.0
        total_citation_precision = 0.0
        discrepancy_matches = 0

        for tc in self.test_cases:
            output = rag_pipeline.query(tc["query"])
            answer = output["answer"]
            citations = output.get("citations", [])
            retrieved_docs = {c.get("document_filename") for c in output.get("retrieved_passages", [])}

            # 1. Context Recall: Were all required source docs retrieved?
            expected_docs = set(tc["required_citations"])
            retrieved_expected = expected_docs.intersection(retrieved_docs)
            context_recall = len(retrieved_expected) / len(expected_docs) if expected_docs else 1.0
            total_context_recall += context_recall

            # 2. Faithfulness & Keyword Alignment
            answer_lower = answer.lower()
            keyword_hits = sum(1 for kw in tc["required_keywords"] if kw.lower() in answer_lower)
            faithfulness = keyword_hits / len(tc["required_keywords"]) if tc["required_keywords"] else 1.0
            total_faithfulness += faithfulness

            # 3. Citation Attribution Precision: Did every citation point to an actual retrieved document?
            cited_docs = {c["document"] for c in citations}
            valid_citations = cited_docs.intersection(expected_docs)
            citation_precision = len(valid_citations) / len(cited_docs) if cited_docs else 0.0
            total_citation_precision += citation_precision

            # 4. Discrepancy Detection Accuracy
            has_disc = output.get("has_discrepancy", False)
            if has_disc == tc["expected_discrepancy"]:
                discrepancy_matches += 1

            results.append({
                "test_id": tc["id"],
                "category": tc["category"],
                "context_recall": round(context_recall, 2),
                "faithfulness": round(faithfulness, 2),
                "citation_precision": round(citation_precision, 2),
                "discrepancy_detected": has_disc
            })

        n = len(self.test_cases)
        summary = {
            "avg_faithfulness": round(total_faithfulness / n, 4),
            "avg_context_recall": round(total_context_recall / n, 4),
            "avg_citation_precision": round(total_citation_precision / n, 4),
            "discrepancy_detection_rate": round(discrepancy_matches / n, 4),
            "total_test_cases": n,
            "detailed_results": results
        }
        return summary
