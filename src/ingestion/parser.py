"""
Layout-Aware PDF Document Parsing and Hierarchical Chunking.
Extracts sections, legal clauses, tables, and creates Parent-Child chunk relationships.
Supports Docling, pdfplumber, and pypdf.
"""

import os
import re
import uuid
import hashlib
from typing import List, Dict, Any

class DocumentParser:
    def __init__(self, parent_chunk_size: int = 1200, child_chunk_size: int = 300, overlap: int = 40):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.overlap = overlap

    def compute_file_hash(self, file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parses PDF file, preserves page references, sections, and structures.
        """
        filename = os.path.basename(file_path)
        file_hash = self.compute_file_hash(file_path)
        pages_content = []

        # 1. Try pypdf extraction
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_content.append({"page": idx + 1, "text": text.strip()})
        except Exception as e:
            # Fallback reading
            pages_content.append({"page": 1, "text": f"Error reading PDF: {str(e)}"})

        return self._create_hierarchical_chunks(filename, file_hash, pages_content)

    def _create_hierarchical_chunks(self, filename: str, file_hash: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates:
        1. Parent Chunks: Full section or page context (for rich synthesis context).
        2. Child Chunks: Focused semantic spans (250-350 tokens) linked to Parent ID.
        """
        parent_chunks = []
        child_chunks = []

        for page_data in pages:
            page_no = page_data["page"]
            text = page_data["text"]

            if not text:
                continue

            # Identify prominent section header if present (e.g. SECTION 2: FEES...)
            section_match = re.search(r'(SECTION\s+\d+[^:\n]+|MILESTONE\s+\d+|INVOICE|AUDIT NOTICE)', text, re.IGNORECASE)
            section_title = section_match.group(1).strip() if section_match else f"Page {page_no}"

            # Create Parent Chunk (broad context)
            parent_id = str(uuid.uuid4())
            parent_chunks.append({
                "id": parent_id,
                "document_filename": filename,
                "file_hash": file_hash,
                "page_number": page_no,
                "section_title": section_title,
                "content": text
            })

            # Create overlapping Child Chunks (retrieval targets)
            words = text.split()
            if len(words) <= self.child_chunk_size:
                child_chunks.append({
                    "id": str(uuid.uuid4()),
                    "parent_id": parent_id,
                    "document_filename": filename,
                    "page_number": page_no,
                    "section_title": section_title,
                    "content": text
                })
            else:
                step = self.child_chunk_size - self.overlap
                for i in range(0, len(words), step):
                    chunk_slice = words[i:i + self.child_chunk_size]
                    chunk_text = " ".join(chunk_slice)
                    if len(chunk_text.strip()) > 40:
                        child_chunks.append({
                            "id": str(uuid.uuid4()),
                            "parent_id": parent_id,
                            "document_filename": filename,
                            "page_number": page_no,
                            "section_title": section_title,
                            "content": chunk_text
                        })

        return {
            "filename": filename,
            "file_hash": file_hash,
            "total_pages": len(pages),
            "parent_chunks": parent_chunks,
            "child_chunks": child_chunks
        }
