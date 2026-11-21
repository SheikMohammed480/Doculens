"""
DocuLens Lex & Ledger: End-to-End Enterprise Demo.
Ingests enterprise contract & invoice PDFs, runs hybrid retrieval,
reranks, generates grounded citations, and displays audit benchmark results.
"""

import os
import glob
from src.ingestion.parser import DocumentParser
from src.embeddings.open_weight_embeddings import OpenWeightEmbedder
from src.db.hybrid_store import HybridStore
from src.retrieval.open_weight_reranker import OpenWeightReranker
from src.generation.open_weight_generator import OpenWeightGenerator
from src.evaluation.eval_benchmark import RAGEvaluationBenchmark

class DocuLensPipeline:
    def __init__(self):
        print("\n[1/5] Initializing DocuLens Open-Weight Pipeline...")
        self.parser = DocumentParser(parent_chunk_size=1200, child_chunk_size=300)
        self.embedder = OpenWeightEmbedder(model_name="BAAI/bge-small-en-v1.5")
        self.store = HybridStore()
        self.reranker = OpenWeightReranker(model_name="BAAI/bge-reranker-base")
        self.generator = OpenWeightGenerator()
        print("      Components loaded: Parser, BGE Embedder (384-d), Hybrid Store, Reranker, Citation Engine.")

    def ingest_documents(self, data_dir: str):
        print(f"\n[2/5] Ingesting & Parsing Enterprise Documents from '{data_dir}'...")
        pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
        if not pdf_files:
            print("      No PDF files found! Running dataset generator...")
            from scripts.generate_sample_dataset import build_msa, build_sow, build_invoice_compliant, build_invoice_disputed
            build_msa()
            build_sow()
            build_invoice_compliant()
            build_invoice_disputed()
            pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))

        total_children = 0
        for pdf_path in pdf_files:
            parsed = self.parser.parse_pdf(pdf_path)
            child_texts = [c["content"] for c in parsed["child_chunks"]]
            embeddings = self.embedder.embed_documents(child_texts)
            self.store.index_document(parsed, embeddings)
            total_children += len(parsed["child_chunks"])
            print(f"      -> Ingested: {parsed['filename']} ({parsed['total_pages']} pages, {len(parsed['parent_chunks'])} parent clauses, {len(parsed['child_chunks'])} child chunks)")

        print(f"      Total indexed: {len(self.store.documents)} documents, {total_children} searchable chunks.")

    def query(self, user_query: str) -> dict:
        # 1. Embed query
        query_embedding = self.embedder.embed_query(user_query)

        # 2. Hybrid Retrieval (Dense HNSW + Sparse BM25 via Reciprocal Rank Fusion)
        retrieved_candidates = self.store.hybrid_search(user_query, query_embedding, top_k=15)

        # 3. Cross-Encoder Reranking
        reranked_top = self.reranker.rerank(user_query, retrieved_candidates, top_k=5)

        # 4. Grounded Citation Generation
        result = self.generator.generate_audit_answer(user_query, reranked_top)
        result["retrieved_passages"] = reranked_top
        return result

def main():
    print("=" * 75)
    print("  DOCULENS LEX & LEDGER: ENTERPRISE CONTRACT & INVOICE RAG SYSTEM")
    print("  100% Open-Weight Stack: BGE Embeddings + Hybrid RRF + Cross-Encoder")
    print("=" * 75)

    pipeline = DocuLensPipeline()
    data_dir = os.path.join(os.path.dirname(__file__), "data", "sample_documents")
    pipeline.ingest_documents(data_dir)

    print("\n[3/5] Running Enterprise Audit Scenarios...")

    # Scenario 1: Cross-Document Discrepancy Detection
    q1 = "Does Invoice INV-2024-099 comply with the late fee and milestone budget terms in the MSA and SOW?"
    print(f"\n--- AUDIT SCENARIO 1: CROSS-DOCUMENT RECONCILIATION ---")
    print(f"Query: {q1}\n")
    out1 = pipeline.query(q1)
    print(out1["answer"])
    print("\nVerified Citations Found:")
    for cit in out1["citations"]:
        print(f"  * {cit['document']} (Page {cit['page']}) -> {cit['section']}")

    # Scenario 2: Legal Liability Inquiry
    q2 = "What is the maximum aggregate liability cap under the MSA, and which claims are uncapped?"
    print(f"\n--- AUDIT SCENARIO 2: LEGAL RISK & LIABILITY ---")
    print(f"Query: {q2}\n")
    out2 = pipeline.query(q2)
    print(out2["answer"])

    # Scenario 3: Automated Benchmark
    print("\n[4/5] Executing Automated Evaluation Benchmark...")
    evaluator = RAGEvaluationBenchmark()
    benchmark_report = evaluator.evaluate_pipeline(pipeline)

    print("\n" + "=" * 75)
    print("                   PORTFOLIO EVALUATION BENCHMARK REPORT")
    print("=" * 75)
    print(f"  Average Faithfulness (Zero Hallucination) : {benchmark_report['avg_faithfulness'] * 100:.1f}%")
    print(f"  Context Recall (Document Retrieval Rate)  : {benchmark_report['avg_context_recall'] * 100:.1f}%")
    print(f"  Citation Attribution Precision            : {benchmark_report['avg_citation_precision'] * 100:.1f}%")
    print(f"  Contract Discrepancy Detection Rate       : {benchmark_report['discrepancy_detection_rate'] * 100:.1f}%")
    print("-" * 75)
    print("  Detailed Test Cases:")
    for res in benchmark_report["detailed_results"]:
        status = "PASSED" if res["faithfulness"] >= 0.8 and res["context_recall"] >= 0.8 else "REVIEW"
        print(f"  [{status}] {res['test_id']} - {res['category']}")
        print(f"          Recall: {res['context_recall']:.2f} | Faithfulness: {res['faithfulness']:.2f} | Citation: {res['citation_precision']:.2f}")
    print("=" * 75)
    print("\n[5/5] Enterprise RAG System is fully operational and benchmarked!\n")

if __name__ == "__main__":
    main()
