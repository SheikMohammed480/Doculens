-- Initialize pgvector and text search extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Document Registry
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default_tenant',
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_type VARCHAR(32) NOT NULL,
    total_pages INT NOT NULL DEFAULT 1,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Parent Chunks (Wide Context for LLM Synthesis)
CREATE TABLE IF NOT EXISTS parent_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    page_start INT NOT NULL,
    page_end INT NOT NULL,
    section_title TEXT,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Child Chunks (Fine-grained Search Units with Vector Embeddings & Lexical Index)
CREATE TABLE IF NOT EXISTS child_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES parent_chunks(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    page_number INT NOT NULL,
    content TEXT NOT NULL,
    tsv_content TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HNSW Vector Index for High-Throughput Approximate Nearest Neighbors
CREATE INDEX IF NOT EXISTS idx_child_chunks_embedding_hnsw 
ON child_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN Index for Full-Text Lexical Search (BM25 Equivalent)
CREATE INDEX IF NOT EXISTS idx_child_chunks_tsv 
ON child_chunks USING gin (tsv_content);

-- Composite B-Tree indexes for fast metadata filtering
CREATE INDEX IF NOT EXISTS idx_child_chunks_doc_page 
ON child_chunks(document_id, page_number);

CREATE INDEX IF NOT EXISTS idx_documents_tenant 
ON documents(tenant_id);
