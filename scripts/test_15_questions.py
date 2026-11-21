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

print(f"Indexed {len(pdf_files)} documents into Hybrid Store.")

# The 15 comprehensive evaluation questions
test_suite = [
    {
        "id": 1,
        "query": "name of the candidate",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Sheik Mohammed"]
    },
    {
        "id": 2,
        "query": "who is the candidate?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Sheik Mohammed", "Computer Science"]
    },
    {
        "id": 3,
        "query": "what are the project he has done ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["EduCrazepolis", "HandPlay Hub"]
    },
    {
        "id": 4,
        "query": "tell me about educrazepolis project",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Django", "MongoDB", "gamification"]
    },
    {
        "id": 5,
        "query": "what is his technical skills ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Java", "Spring", "SQL"]
    },
    {
        "id": 6,
        "query": "what are the programming languages he knows ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Java", "C++", "Python"]
    },
    {
        "id": 7,
        "query": "where is he currently working ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Zlendo", "Junior AI Engineer"]
    },
    {
        "id": 8,
        "query": "what is his work experience and internship ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Zlendo", "Elysium", "Sputnik"]
    },
    {
        "id": 9,
        "query": "tell me about his education and college",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Sethu Institute of Technology", "Computer Science"]
    },
    {
        "id": 10,
        "query": "what is his CGPA ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["8.8"]
    },
    {
        "id": 11,
        "query": "what languages can he speak and what is his fluency ?",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["Tamil", "English", "Fluent"]
    },
    {
        "id": 12,
        "query": "how can i contact him? email and phone",
        "target_doc": "Sheik_Mohammed_Resume.pdf",
        "expected_keywords": ["sheikmohammed480@gmail.com", "7904119125"]
    },
    {
        "id": 13,
        "query": "audit discrepancies in INV-099",
        "target_doc": "INV_2024_099_Disputed.pdf",
        "expected_keywords": ["210", "175", "2,800"]
    },
    {
        "id": 14,
        "query": "is invoice INV-081 compliant with the contract?",
        "target_doc": "INV_2024_081_Compliant.pdf",
        "expected_keywords": ["compliant", "150", "165"]
    },
    {
        "id": 15,
        "query": "what is the limitation of liability cap under the agreement?",
        "target_doc": "MSA_Acme_Cyberdyne_2024.pdf",
        "expected_keywords": ["12", "liability", "cap"]
    }
]

print(f"\nRunning 15 Comprehensive Questions Evaluation...\n" + "="*80)

passed = 0
for tc in test_suite:
    q = tc["query"]
    target = tc["target_doc"]
    q_emb = embedder.embed_query(q)
    cand = store.hybrid_search(q, q_emb, top_k=5, target_document=target)
    top = reranker.rerank(q, cand, top_k=3)
    res = generator.generate_audit_answer(q, top)
    ans = res["answer"]
    
    # Check expected keywords
    has_all = all(kw.lower() in ans.lower() for kw in tc["expected_keywords"])
    status = "PASS" if has_all else "FAIL"
    if has_all: passed += 1
    
    print(f"[{status}] Q{tc['id']:02d}: {q}")
    print(f"       Expected: {tc['expected_keywords']}")
    print(f"       Preview: {ans.replace(chr(10), ' ')[:140]}...")
    print("-" * 80)

print(f"\nFINAL RESULT: {passed}/{len(test_suite)} Questions Passed.")
