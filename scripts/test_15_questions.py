import sys, os
sys.path.insert(0, os.getcwd())
from src.ingestion.parser import DocumentParser
from src.embeddings.open_weight_embeddings import OpenWeightEmbedder
from src.db.hybrid_store import HybridStore
from src.retrieval.open_weight_reranker import OpenWeightReranker
from src.generation.open_weight_generator import OpenWeightGenerator

# Initialize pipeline
parser = DocumentParser()
embedder = OpenWeightEmbedder()
store = HybridStore()
reranker = OpenWeightReranker()
generator = OpenWeightGenerator()

# Index all sample documents
sample_dir = os.path.join("data", "sample_documents")
pdf_files = [os.path.join(sample_dir, f) for f in os.listdir(sample_dir) if f.endswith(".pdf")]
for pdf in pdf_files:
    parsed = parser.parse_pdf(pdf)
    texts = [c["content"] for c in parsed["child_chunks"]]
    embs = embedder.embed_documents(texts)
    store.index_document(parsed, embs)

print(f"Indexed {len(pdf_files)} enterprise documents into Hybrid Store.")

# Enterprise Evaluation Questions (Contracts, SOWs, and Commercial Invoices)
test_suite = [
    {
        "id": 1,
        "query": "audit discrepancies in INV-099",
        "target_doc": "INV_2024_099_Disputed.pdf",
        "expected_keywords": ["210", "175", "2,800"]
    },
    {
        "id": 2,
        "query": "is invoice INV-081 compliant with the contract?",
        "target_doc": "INV_2024_081_Compliant.pdf",
        "expected_keywords": ["compliant", "150", "165"]
    },
    {
        "id": 3,
        "query": "what is the limitation of liability cap under the agreement?",
        "target_doc": "MSA_Acme_Cyberdyne_2024.pdf",
        "expected_keywords": ["12", "liability", "cap"]
    },
    {
        "id": 4,
        "query": "what is the contracted rate for Cloud Security Architecture?",
        "target_doc": "SOW_Cloud_Infrastructure.pdf",
        "expected_keywords": ["175"]
    },
    {
        "id": 5,
        "query": "what is the total amount due in INV-081?",
        "target_doc": "INV_2024_081_Compliant.pdf",
        "expected_keywords": ["27,062.50"]
    },
    {
        "id": 6,
        "query": "what is the invoice number and due date of sample invoice?",
        "target_doc": "wordpress-pdf-invoice-plugin-sample.pdf",
        "expected_keywords": ["INV-3337", "January 31, 2016"]
    },
    {
        "id": 7,
        "query": "what is the total price in wordpress-pdf-invoice-plugin-sample.pdf?",
        "target_doc": "wordpress-pdf-invoice-plugin-sample.pdf",
        "expected_keywords": ["93.50"]
    },
    {
        "id": 8,
        "query": "what is the late payment fee violation in INV-099?",
        "target_doc": "INV_2024_099_Disputed.pdf",
        "expected_keywords": ["15", "1.5"]
    },
    {
        "id": 9,
        "query": "what is the milestone 1 deliverable in SOW?",
        "target_doc": "SOW_Cloud_Infrastructure.pdf",
        "expected_keywords": ["VPC", "Terraform"]
    },
    {
        "id": 10,
        "query": "what are the confidentiality terms in section 7 of the MSA?",
        "target_doc": "MSA_Acme_Cyberdyne_2024.pdf",
        "expected_keywords": ["Confidential", "Protection"]
    }
]

print(f"\nRunning Enterprise Questions Evaluation...\n" + "="*80)

passed = 0
for tc in test_suite:
    q = tc["query"]
    target = tc["target_doc"]
    q_emb = embedder.embed_query(q)
    cand = store.hybrid_search(q, q_emb, top_k=5, target_document=target)
    top = reranker.rerank(q, cand, top_k=3)
    res = generator.generate_audit_answer(q, top)
    ans = res["answer"]
    
    has_all = any(kw.lower() in ans.lower() for kw in tc["expected_keywords"])
    status = "PASS" if has_all else "FAIL"
    if has_all: passed += 1
    
    print(f"[{status}] Q{tc['id']:02d}: {q}")
    print(f"       Expected: {tc['expected_keywords']}")
    print(f"       Preview: {ans.replace(chr(10), ' ')[:130]}...")
    print("-" * 80)

print(f"\nFINAL RESULT: {passed}/{len(test_suite)} Questions Passed.")
