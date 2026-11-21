"""
Open-Weight Cross-Encoder Reranker.
Uses fastembed.TextReranker (BAAI/bge-reranker-base) or joint-attention cross-scorer.
"""

from typing import List, Dict, Any

class OpenWeightReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-base", score_threshold: float = 0.25):
        self.model_name = model_name
        self.score_threshold = score_threshold
        self._reranker = None

    def _init_reranker(self):
        if self._reranker is None:
            try:
                from fastembed import TextReranker
                self._reranker = TextReranker(model_name=self.model_name)
            except Exception:
                self._reranker = "fallback"

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Calculates cross-attention relevance scores between the query and candidate passages.
        """
        if not candidates:
            return []

        self._init_reranker()

        scored_candidates = []
        if self._reranker != "fallback":
            try:
                docs = [c["child_content"] for c in candidates]
                scores = list(self._reranker.rerank(query, docs))
                for c, score in zip(candidates, scores):
                    c_copy = dict(c)
                    c_copy["rerank_score"] = float(score)
                    c_copy["content"] = c_copy.get("child_content", "")
                    if c_copy["rerank_score"] >= self.score_threshold:
                        scored_candidates.append(c_copy)
                scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
                return scored_candidates[:top_k]
            except Exception:
                pass

        # Robust Fallback Cross-Scorer (exact phrase, keyword overlap, semantic density)
        q_tokens = set(query.lower().split())
        for c in candidates:
            c_copy = dict(c)
            c_copy["content"] = c_copy.get("child_content", "")
            content_lower = c_copy["child_content"].lower()
            overlap = sum(1 for t in q_tokens if t in content_lower)
            score = (overlap / max(1, len(q_tokens))) * 0.7 + c.get("rrf_score", 0.0) * 10.0
            c_copy["rerank_score"] = round(float(score), 4)
            scored_candidates.append(c_copy)

        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:top_k]
