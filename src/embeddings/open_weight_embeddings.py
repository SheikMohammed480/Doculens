"""
Open-Weight Embedding Model Wrapper.
Uses BAAI/bge-small-en-v1.5 (384 dimensions) via fastembed/onnxruntime,
with graceful deterministic fallback.
"""

from typing import List
import numpy as np

class OpenWeightEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self.dimension = 384

    def _init_model(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name)
            except Exception:
                self._model = "fallback"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        self._init_model()
        if self._model != "fallback":
            try:
                # Fastembed returns a generator of numpy arrays
                embeddings = list(self._model.embed(texts))
                return [arr.tolist() for arr in embeddings]
            except Exception:
                pass

        # Robust deterministic fallback embedding (384-dim normalized vector)
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.embed_documents([query])[0]

    def _fallback_embed(self, text: str) -> List[float]:
        """
        Deterministic hash projection into 384 dimensions for fallback/offline testing.
        """
        import hashlib
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            dim_idx = h % self.dimension
            weight = 1.0 / (1.0 + 0.1 * idx)
            vec[dim_idx] += (1.0 if (h & 1) else -1.0) * weight
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
