"""
Strict Grounded LLM Generation Engine with Sentence-Level Citations.
"""

from typing import List, Dict, Any, Generator
import json

SYSTEM_PROMPT = """You are an Enterprise Compliance and Financial Document Intelligence AI.
Answer the user's question STRICTLY based on the provided reference passages.

RULES:
1. Every factual assertion MUST include a citation bracket: [Doc: <filename>, Page: <page_no>].
2. If the answer cannot be determined with certainty from the provided passages, state clearly:
   "Based on the provided documents, there is insufficient evidence to determine [topic]."
   NEVER speculate or use external knowledge.
3. If extracting financial numbers or metrics from tables, maintain exact figures and footnote conditions.
"""

class CitationGenerator:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def build_context_prompt(self, query: str, passages: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, p in enumerate(passages, 1):
            doc_name = p.get("document_filename", "Document")
            page_no = p.get("page_number", "Unknown")
            # Prefer parent content for richer narrative context
            content = p.get("parent_content") or p.get("child_content", "")
            context_blocks.append(f"--- PASSAGE {idx} [Doc: {doc_name}, Page: {page_no}] ---\n{content}\n")

        joined_context = "\n".join(context_blocks)
        return f"REFERENCE PASSAGES:\n{joined_context}\n\nUSER QUESTION: {query}\n\nANSWER WITH CITATIONS:"

    def generate_answer(self, query: str, passages: List[Dict[str, Any]]) -> str:
        """
        Executes grounded synthesis using OpenAI or compatible LLM provider.
        """
        import os
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        user_prompt = self.build_context_prompt(query, passages)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
