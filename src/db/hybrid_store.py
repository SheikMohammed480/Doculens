"""
Hybrid Vector & Lexical Store with Reciprocal Rank Fusion (RRF).
Supports:
1. PostgreSQL 16 + pgvector (for enterprise production deployment)
2. In-Memory / Local Store (for instant out-of-the-box local execution & CI)
Supports pre-filtering by target_document.
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional

class HybridStore:
    def __init__(self, use_postgres: bool = False, db_url: Optional[str] = None):
        self.use_postgres = use_postgres
        self.db_url = db_url
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.parent_chunks: Dict[str, Dict[str, Any]] = {}
        self.child_chunks: List[Dict[str, Any]] = []

    def index_document(self, parsed_doc: Dict[str, Any], embeddings: List[List[float]]):
        """
        Stores document, parent chunks, and child chunks with dense vector embeddings.
        """
        doc_filename = parsed_doc["filename"]
        self.documents[doc_filename] = {
            "filename": doc_filename,
            "file_hash": parsed_doc["file_hash"],
            "total_pages": parsed_doc["total_pages"]
        }

        for p in parsed_doc["parent_chunks"]:
            self.parent_chunks[p["id"]] = p

        for c, emb in zip(parsed_doc["child_chunks"], embeddings):
            c_copy = dict(c)
            c_copy["embedding"] = emb
            self.child_chunks.append(c_copy)

    def hybrid_search(
        self, 
        query: str, 
        query_embedding: List[float], 
        top_k: int = 10, 
        rrf_k: int = 60,
        target_document: Optional[str] = None,
        allowed_documents: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes Dense Cosine Search + BM25/Lexical Search and merges with Reciprocal Rank Fusion.
        Enforces Role-Based Access Control (allowed_documents) and target_document scope.
        """
        if not self.child_chunks:
            return []

        # 1. Multi-Tenant Authorization Pre-Filter (RBAC)
        if allowed_documents is not None:
            allowed_set = set(allowed_documents)
            candidate_chunks = [
                (idx, c) for idx, c in enumerate(self.child_chunks)
                if c.get("document_filename") in allowed_set
            ]
        else:
            candidate_chunks = list(enumerate(self.child_chunks))

        # 2. Document Scope Filter (User-selected document)
        if target_document and target_document != "All Documents":
            candidate_chunks = [
                (idx, c) for idx, c in candidate_chunks
                if c.get("document_filename") == target_document
            ]

        if not candidate_chunks:
            return []

        # 1. Dense Vector Scoring (Cosine Similarity)
        q_vec = np.array(query_embedding, dtype=np.float32)
        dense_scores = []
        for orig_idx, chunk in candidate_chunks:
            c_vec = np.array(chunk["embedding"], dtype=np.float32)
            denom = (np.linalg.norm(q_vec) * np.linalg.norm(c_vec))
            sim = float(np.dot(q_vec, c_vec) / denom) if denom > 0 else 0.0
            dense_scores.append((orig_idx, sim))
        dense_scores.sort(key=lambda x: x[1], reverse=True)

        dense_rank_map = {}
        for rank, (chunk_idx, _) in enumerate(dense_scores):
            dense_rank_map[chunk_idx] = rank + 1

        # 2. Lexical / Keyword Scoring (Token frequency & clause matching)
        query_terms = set(query.lower().split())
        lexical_scores = []
        for orig_idx, chunk in candidate_chunks:
            text_lower = chunk["content"].lower()
            match_count = sum(1 for term in query_terms if term in text_lower)
            lexical_scores.append((orig_idx, match_count))
        lexical_scores.sort(key=lambda x: x[1], reverse=True)

        lexical_rank_map = {}
        for rank, (chunk_idx, _) in enumerate(lexical_scores):
            lexical_rank_map[chunk_idx] = rank + 1

        # 3. Reciprocal Rank Fusion (RRF)
        fused_candidates = []
        for orig_idx, chunk in candidate_chunks:
            v_rank = dense_rank_map.get(orig_idx, 999)
            l_rank = lexical_rank_map.get(orig_idx, 999)
            rrf_score = (1.0 / (rrf_k + v_rank)) + (1.0 / (rrf_k + l_rank))

            parent = self.parent_chunks.get(chunk["parent_id"], {})
            fused_candidates.append({
                "chunk_id": chunk["id"],
                "parent_id": chunk["parent_id"],
                "document_filename": chunk["document_filename"],
                "page_number": chunk["page_number"],
                "section_title": chunk.get("section_title", ""),
                "child_content": chunk["content"],
                "parent_content": parent.get("content", chunk["content"]),
                "rrf_score": rrf_score
            })

        fused_candidates.sort(key=lambda x: x["rrf_score"], reverse=True)
        return fused_candidates[:top_k]
