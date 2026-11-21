import os
from src.ingestion.parser import DocumentParser
from src.embeddings.open_weight_embeddings import OpenWeightEmbedder
from src.db.hybrid_store import HybridStore
from src.retrieval.open_weight_reranker import OpenWeightReranker
from src.generation.open_weight_generator import OpenWeightGenerator

def main():
    resume_path = os.path.join("data", "sample_documents", "Sheik_Mohammed_Resume.pdf")
    if not os.path.exists(resume_path):
        print(f"File not found: {resume_path}")
        return

    print(f"Ingesting: {resume_path} ...")
    parser = DocumentParser()
    embedder = OpenWeightEmbedder()
    store = HybridStore()
    reranker = OpenWeightReranker()
    generator = OpenWeightGenerator(ollama_model="qwen2.5:1.5b")

    parsed = parser.parse_pdf(resume_path)
    child_texts = [c["content"] for c in parsed["child_chunks"]]
    embeddings = embedder.embed_documents(child_texts)
    store.index_document(parsed, embeddings)
    print(f"Indexed successfully: {len(parsed['child_chunks'])} chunks.")

    # Test Query 1: Overview & Skills
    queries = [
        "Give me a professional summary of Sheik Mohammed, his technical skills, and experience.",
        "What projects or engineering achievements are listed on this resume?"
    ]

    for q in queries:
        print("\n" + "="*70)
        print(f"QUERY: {q}")
        print("="*70)
        q_emb = embedder.embed_query(q)
        candidates = store.hybrid_search(q, q_emb, top_k=5)
        reranked = reranker.rerank(q, candidates, top_k=3)
        res = generator.generate_audit_answer(q, reranked)

        print("\n[SYNTHESIZED ANSWER]:")
        print(res["answer"])
        print("\n[CITATIONS]:")
        for cit in res["citations"]:
            print(f"  * {cit['document']} (Page {cit['page']})")

if __name__ == "__main__":
    main()
