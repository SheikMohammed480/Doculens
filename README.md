---
title: Doculens
emoji: 🐨
colorFrom: green
colorTo: purple
sdk: gradio
sdk_version: 6.32.0
python_version: '3.12'
app_file: app.py
pinned: false
license: mit
---

# DocuLens Lex & Ledger: Open-Weight Document Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Open-Weight Embeddings](https://img.shields.io/badge/Embeddings-BAAI%2Fbge--small--en--v1.5-green.svg)](https://huggingface.co/BAAI/bge-small-en-v1.5)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_pgvector-blue.svg)](https://github.com/pgvector/pgvector)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a389.svg)](https://fastapi.tiangolo.com)
[![Docker Ready](https://img.shields.io/badge/Docker-Self--Contained-blue.svg)](Dockerfile)
[![Benchmark](https://img.shields.io/badge/Benchmark-100%25_Verified-success.svg)](#portfolio-evaluation-benchmark-report)

**DocuLens Lex & Ledger** is an enterprise-grade, **100% open-weight** Document Intelligence and Retrieval-Augmented Generation (RAG) platform. It provides automated document analysis, contract auditing, commercial invoice reconciliation, and resume reasoning with exact sentence-level page citations.

**Key Advantages:**
- **Zero Cloud API Fees**: Runs with open-weight models (`Qwen 2.5`, `BGE-small`, `BGE-reranker`) — **No OpenAI, Gemini, or external API keys needed**.
- **Tenant Isolation & RBAC**: Users create accounts and can only view/query their own uploaded documents.
- **Cross-Document Discrepancy Detection**: Catches unapproved billing items, fee violations, and milestone cap breaches between invoices and Master Services Agreements.
- **Two-Stage Hybrid Search**: Dense Vector Search + BM25 Lexical Matching fused via Reciprocal Rank Fusion (RRF $k=60$) followed by Cross-Encoder Joint-Attention Reranking.

---

## 🏛️ System Architecture

```
Enterprise PDF Documents (Resumes, MSAs, SOWs, Invoices)
                       │
                       ▼
            [1. Layout-Aware Parser]
         (Preserves Tables, §§, and Clauses)
                       │
                       ▼
          [2. Hierarchical Chunking]
         ┌─────────────┴─────────────┐
         ▼                           ▼
   Parent Clauses              Child Chunks
 (Wide Context Window)      (384-d Search Units)
         │                           │
         │                           ▼
         │               [3. Open-Weight BGE Embedder]
         │                 (BAAI/bge-small-en-v1.5)
         │                           │
         ▼                           ▼
[PostgreSQL 16 + pgvector / Local In-Memory Hybrid Store]
  ◄── HNSW Vector Index (vector_cosine_ops) + BM25 Lexical Index
                       │
                       ▼
        [4. Hybrid Retrieval with RRF]
   (Pre-retrieval Tenant Authorization Filter)
                       │
                       ▼
       [5. Cross-Encoder Joint Reranker]
           (BAAI/bge-reranker-base)
                       │
                       ▼
       [6. Grounded Synthesis & Citations]
    (Local Qwen 2.5 with Zero-Hallucination Guardrails)
                       │
                       ▼
        [7. Automated Audit Evaluation]
    (Faithfulness, Recall, Citation Precision)
```

---

## 🔐 Multi-Tenant Role-Based Access Control (RBAC)

The system enforces strict tenant isolation using SQLite (`data/enterprise_auth.db`) and salted `PBKDF2-HMAC-SHA256` password hashing with JWT Bearer tokens:

| Identity | Role | Default Password | Document Clearance |
| :--- | :--- | :--- | :--- |
| **`admin`** | **Admin** | `admin123` | **Master Admin Account** — Full access to all 5 documents & evaluation benchmarks. |
| **`auditor`** | **Auditor** | `auditor123` | **Testing Demo Account** — Access to commercial contracts (`MSA`, `SOW`) and tax invoices (`INV-081`, `INV-099`). |
| **New User** | **User** | Custom | **Tenant-Isolated Account** — Starts with 0 documents. Can only view and search documents they personally upload. |

---

## 📊 Portfolio Evaluation Benchmark Report

Measured via the automated evaluation harness [`src/evaluation/eval_benchmark.py`](file:///d:/RAG/src/evaluation/eval_benchmark.py):

| Metric | Baseline Naive RAG | DocuLens Lex & Ledger | Delta |
| :--- | :---: | :---: | :---: |
| **Faithfulness (Zero Hallucination)** | 62.5% | **100.0%** | **+37.5%** |
| **Context Recall (Document Hit Rate)** | 55.0% | **100.0%** | **+45.0%** |
| **Citation Attribution Precision** | 40.0% | **100.0%** | **+60.0%** |
| **Contract Discrepancy Catch Rate** | 0.0% | **100.0%** | **+100.0%** |
| **Private / On-Premise Deployable** | ❌ (Cloud API) | **✅ (100% Open-Weight)** | Sovereign |

---

## 🚀 Free Cloud Deployment (Zero API Keys & Zero Laptop Dependency)

The repository includes a self-contained [`Dockerfile`](file:///d:/RAG/Dockerfile) with **embedded Ollama + Qwen 2.5**, meaning the model runs **inside the cloud container for free with ZERO API keys**:

### 1-Click Free Deployment on Hugging Face Spaces (16GB RAM Free Tier)
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Docker** (Blank) and choose the **Free Tier (16 GB RAM, 2 vCPU)**.
3. Link your GitHub repository: `https://github.com/SheikMohammed480/Doculens`.
4. Hugging Face builds the Docker container, boots the embedded Ollama engine, pulls `qwen2.5:1.5b`, and serves your app live at `https://huggingface.co/spaces/SheikMohammed480/Doculens`!
5. **No API keys needed, laptop can be completely shut down, 100% free forever.**

---

## 🖥️ Local Quickstart

### 1. Run the FastAPI Modern Studio (Port 8000)
```powershell
py -3.10 app.py
```
> Access dashboard at **`http://127.0.0.1:8000`** (or REST API docs at `http://127.0.0.1:8000/docs`).

### 2. Run the Streamlit Dashboard (Port 8501)
```powershell
py -3.10 -m streamlit run streamlit_app.py --server.port 8501
```
> Access dashboard at **`http://localhost:8501`**.

---

## 🚀 Live Cloud Deployment & Production Links

The platform is deployed live on **Hugging Face Spaces** (Free Cloud Tier, Zero API Keys, Zero Laptop Hardware):

- **🌐 Live Production Studio**: [https://sheik11111-doculens.hf.space/static/index.html](https://sheik11111-doculens.hf.space/static/index.html)
- **🤗 Hugging Face Space**: [https://huggingface.co/spaces/sheik11111/Doculens](https://huggingface.co/spaces/sheik11111/Doculens)
- **📖 Comprehensive Deployment & Troubleshooting Guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full documentation on platform choices, model runtime details, and the 6 engineering challenges resolved during deployment.

### 🔐 Multi-Tenant Login Credentials
- **System Admin**: `admin` / `admin123` (Full clearance across all documents and evaluation benchmarks)
- **Auditor (1-Click Demo)**: `auditor` / `auditor123` (Pre-seeded with commercial contracts and disputed invoices)
- **New User**: Click "Register" to create an isolated personal workspace.

---

## 📁 Repository Structure

```
Doculens/
├── app.py                      # FastAPI Application with RBAC & Static File Routing
├── streamlit_app.py            # Streamlit Studio Dashboard
├── Dockerfile                  # Self-contained container (Ollama + Qwen + FastAPI)
├── start.sh                    # Container bootstrapper script
├── requirements.txt            # Production Python dependencies
├── DOCULENS_ARCHITECTURE_GUIDE.md # Detailed Architecture & Interview Q&A
├── DEPLOYMENT_GUIDE.md         # Deployment & Free Hosting Blueprint
├── static/
│   ├── index.html              # Glassmorphism Tailwind UI
│   └── app.js                  # Pure ES6+ Controller
├── src/
│   ├── auth/                   # SQLite Multi-Tenant RBAC & JWT Tokens
│   ├── ingestion/              # Table-preserving parser & Parent/Child chunker
│   ├── embeddings/             # BAAI/bge-small-en-v1.5 Dense Embedder
│   ├── db/                     # Hybrid Store (HNSW Vector + BM25 Lexical with RRF)
│   ├── retrieval/              # Cross-Encoder Reranker (BAAI/bge-reranker-base)
│   ├── generation/             # Open-Weight LLM Synthesis & Discrepancy Detection
│   └── evaluation/             # Automated RAG Triad Evaluation Suite
└── data/sample_documents/      # Pre-loaded MSA, SOW, and Invoices
```
