"""
Open-Weight Grounded Synthesis & Multi-Document RAG Engine.
Automatically detects local Ollama open-weight LLMs (qwen2.5:1.5b / qwen2.5:3b / llama3.2).
Generates fluent, synthesized paragraphs and answers grounded in retrieved passages with exact citations.
"""

import os
import re
import json
import urllib.request
from typing import List, Dict, Any, Optional

class OpenWeightGenerator:
    def __init__(self, ollama_model: str = "qwen2.5:1.5b", ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_model = os.environ.get("GROQ_MODEL", "qwen-2.5-32b")
        self.active_model = self._detect_available_model() or ollama_model
        self.ollama_model = self.active_model

    def _detect_available_model(self) -> str:
        """
        Dynamically detects available open-weight models:
        1. If GROQ_API_KEY is configured in cloud environment, uses Groq open-weight models.
        2. Otherwise detects installed local Ollama models (qwen2.5:1.5b / qwen2.5:3b / llama3.2).
        """
        if self.groq_api_key:
            return f"Groq Cloud: {self.groq_model}"

        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                installed = [m.get("name") for m in data.get("models", [])]
                for preferred in ["qwen2.5:1.5b", "qwen2.5:3b", "llama3.2:3b", "llama3.2:latest", "llama3.1:8b", "mistral:latest"]:
                    for m in installed:
                        if preferred in m:
                            return m
                if installed:
                    return installed[0]
        except Exception:
            pass
        return "qwen2.5:1.5b"

    def generate_audit_answer(self, query: str, context_passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes an intelligent, fluent answer with citations for ANY document.
        """
        if not context_passages:
            return {
                "query": query,
                "answer": "Based on the provided documents, no relevant passages were found to answer your inquiry.",
                "citations": [],
                "has_discrepancy": False,
                "retrieved_passages_count": 0,
                "model_used": self.active_model
            }

        # 1. Generate fluent synthesis using local Open-Weight LLM
        answer_text = self._try_ollama_generation(query, context_passages)

        # 2. Extract verified citation tags from answer
        citations = re.findall(r'\[Doc:\s*([^,\]]+),\s*Page:\s*(\d+)(?:,\s*([^\]]+))?\]', answer_text)
        formatted_citations = [
            {"document": c[0].strip(), "page": int(c[1]), "section": c[2].strip() if c[2] else ""}
            for c in citations
        ]

        # Ensure citations exist
        if not formatted_citations and context_passages:
            top_p = context_passages[0]
            answer_text += f"\n\n[Doc: {top_p.get('document_filename')}, Page: {top_p.get('page_number')}]"
            formatted_citations.append({
                "document": top_p.get("document_filename"),
                "page": top_p.get("page_number"),
                "section": top_p.get("section_title", "")
            })

        # Check for contractual discrepancy / violation flags
        lower_ans = answer_text.lower()
        has_discrepancy = (
            "non-compliant" in lower_ans or 
            "does not comply" in lower_ans or
            "discrepancy" in lower_ans or 
            "violation" in lower_ans or
            "violates" in lower_ans or
            "overcharge" in lower_ans or
            "exceeds" in lower_ans or
            "breach" in lower_ans
        )

        return {
            "query": query,
            "answer": answer_text,
            "citations": formatted_citations,
            "has_discrepancy": has_discrepancy,
            "retrieved_passages_count": len(context_passages),
            "model_used": self.active_model
        }

    def _try_ollama_generation(self, query: str, passages: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, p in enumerate(passages[:4], 1):
            doc = p.get("document_filename", "Document")
            page = p.get("page_number", 1)
            content = p.get("child_content") or p.get("parent_content", "")
            context_blocks.append(f"--- SOURCE EXCERPT {idx} [Document: {doc}, Page: {page}] ---\n{content}\n")

        joined_context = "\n".join(context_blocks)

        system_prompt = (
            "You are an advanced Enterprise Document Intelligence Assistant.\n"
            "Your task is to answer the user's question accurately, directly, and professionally based strictly on the provided source excerpts.\n\n"
            "INSTRUCTIONS:\n"
            "1. Answer ONLY what the user asks. Do NOT repeat or dump unrelated document text (such as unrequested contacts, unrelated education, or other sections).\n"
            "2. If asked about projects, experience, or skills, synthesize a clean, coherent summary using bullet points or concise paragraphs.\n"
            "3. If auditing contracts or invoices, clearly highlight discrepancies or overcharges.\n"
            "4. Append the citation at the end in the format: [Doc: <filename>, Page: <page_no>].\n"
            "5. Never hallucinate or invent facts not present in the excerpts."
        )

        user_content = (
            f"REFERENCE EXCERPTS:\n{joined_context}\n\n"
            f"USER INQUIRY: {query}\n\n"
            f"Direct Answer with Citations:"
        )

        # 1. Cloud-Native Option: Groq Free Open-Weight API (when deployed to cloud)
        if self.groq_api_key:
            try:
                groq_payload = {
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 450
                }
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(groq_payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.groq_api_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            except Exception as e:
                pass

        # 2. Local-Native Option: Local Ollama on CUDA GPU (when running on host)
        payload = {
            "model": self.active_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 4096,
                "num_predict": 350
            }
        }

        try:
            req = urllib.request.Request(
                f"{self.ollama_url}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode())
                return data.get("message", {}).get("content", "").strip()
        except Exception:
            # Fallback only if local Ollama process is unreachable
            return self._fallback_synthesis(query, passages)

    def _fallback_synthesis(self, query: str, passages: List[Dict[str, Any]]) -> str:
        top_p = passages[0] if passages else {}
        return (
            f"According to {top_p.get('document_filename')} (Page {top_p.get('page_number')}):\n"
            f"{top_p.get('child_content', '')}\n\n"
            f"[Doc: {top_p.get('document_filename')}, Page: {top_p.get('page_number')}]"
        )
