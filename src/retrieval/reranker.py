from typing import List, Dict, Any

class CrossEncoderReranker:
    """
    Reranks candidate retrieved chunks using a Cross-Encoder model
    to model query-passage cross-attention.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-large", score_threshold: float = 0.40):
        self.model_name = model_name
        self.score_threshold = score_threshold
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except ImportError:
                raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Computes relevance scores for (query, passage) pairs, sorts, and filters.
        """
        if not candidates:
            return []

        self._load_model()

        # Prepare pairs: use child content for precise scoring, or parent if preferred
        sentence_pairs = [[query, item.get("child_content", "")] for item in candidates]
        scores = self._model.predict(sentence_pairs)

        reranked_items = []
        for item, score in zip(candidates, scores):
            item_copy = dict(item)
            item_copy["rerank_score"] = float(score)
            if item_copy["rerank_score"] >= self.score_threshold:
                reranked_items.append(item_copy)

        # Sort descending by score
        reranked_items.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked_items[:top_k]
