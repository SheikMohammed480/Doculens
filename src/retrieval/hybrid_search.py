from typing import List, Dict, Any, Optional
import psycopg
from psycopg.rows import dict_row

class HybridRetriever:
    """
    Executes hybrid retrieval combining Dense Vector Search (HNSW)
    and Sparse Lexical Search (tsvector) using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, db_url: str):
        self.db_url = db_url

    def search(
        self,
        query_text: str,
        query_embedding: List[float],
        allowed_doc_ids: Optional[List[str]] = None,
        top_k: int = 25,
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search query and retrieves candidates with parent context.
        """
        sql_query = """
        WITH vector_search AS (
            SELECT 
                c.id, c.parent_id, c.document_id, c.content, c.page_number,
                ROW_NUMBER() OVER (ORDER BY c.embedding <=> %(embedding)s::vector) AS vector_rank
            FROM child_chunks c
            WHERE (%(allowed_doc_ids)s::uuid[] IS NULL OR c.document_id = ANY(%(allowed_doc_ids)s::uuid[]))
            ORDER BY c.embedding <=> %(embedding)s::vector
            LIMIT %(candidate_limit)s
        ),
        lexical_search AS (
            SELECT 
                c.id, c.parent_id, c.document_id, c.content, c.page_number,
                ROW_NUMBER() OVER (ORDER BY ts_rank_cd(c.tsv_content, websearch_to_tsquery('english', %(query_text)s)) DESC) AS lexical_rank
            FROM child_chunks c
            WHERE c.tsv_content @@ websearch_to_tsquery('english', %(query_text)s)
              AND (%(allowed_doc_ids)s::uuid[] IS NULL OR c.document_id = ANY(%(allowed_doc_ids)s::uuid[]))
            ORDER BY ts_rank_cd(c.tsv_content, websearch_to_tsquery('english', %(query_text)s)) DESC
            LIMIT %(candidate_limit)s
        )
        SELECT 
            COALESCE(v.id, l.id) AS chunk_id,
            COALESCE(v.parent_id, l.parent_id) AS parent_id,
            COALESCE(v.document_id, l.document_id) AS document_id,
            COALESCE(v.content, l.content) AS child_content,
            COALESCE(v.page_number, l.page_number) AS page_number,
            d.filename AS document_filename,
            p.content AS parent_content,
            (COALESCE(1.0 / (%(rrf_k)s + v.vector_rank), 0.0) + 
             COALESCE(1.0 / (%(rrf_k)s + l.lexical_rank), 0.0)) AS rrf_score
        FROM vector_search v
        FULL OUTER JOIN lexical_search l ON v.id = l.id
        JOIN documents d ON d.id = COALESCE(v.document_id, l.document_id)
        JOIN parent_chunks p ON p.id = COALESCE(v.parent_id, l.parent_id)
        ORDER BY rrf_score DESC
        LIMIT %(top_k)s;
        """

        params = {
            "embedding": query_embedding,
            "query_text": query_text,
            "allowed_doc_ids": allowed_doc_ids,
            "candidate_limit": top_k * 2,
            "rrf_k": rrf_k,
            "top_k": top_k,
        }

        with psycopg.connect(self.db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, params)
                results = cur.fetchall()
                return results
