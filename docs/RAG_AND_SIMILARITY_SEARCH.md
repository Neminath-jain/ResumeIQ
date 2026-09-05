# RAG, Vector Similarity Search & LangChain Architecture

## Overview

This document details the Retrieval-Augmented Generation (RAG), Vector Embedding, and Similarity Search architecture implemented in the **AI Resume Analyzer & ATS Job Matcher (ResumeIQ)**.

---

## 1. Executive Summary

The project implements a hybrid skill matching architecture that goes beyond traditional naive keyword string comparison:
1. **Role Inference & Extraction:** Supports detailed job descriptions and short target role titles (e.g., *"Full Stack Engineer"*, *"Data Analyst"*), automatically inferring 8–12 standard required skills, preferred tools, and experience levels.
2. **Compound Skill Variant Decomposition (`get_skill_variants`):** Decomposes complex skill phrases, parentheses, and conjunctions (e.g. `SQL (PostgreSQL, MySQL)` $\rightarrow$ `sql`, `postgresql`, `mysql`; `TensorFlow or PyTorch` $\rightarrow$ `tensorflow`, `pytorch`).
3. **Bidirectional Technology Aliases (`TECH_ALIASES`):** Resolves bidirectional acronyms and synonyms (e.g. `k8s` $\leftrightarrow$ `kubernetes`, `ml` $\leftrightarrow$ `machine learning`, `reactjs` / `react.js` $\leftrightarrow$ `react`, `golang` $\leftrightarrow$ `go`, `aws` $\leftrightarrow$ `amazon web services`).
4. **Dense Vector Embeddings & Similarity Search:** Uses `sentence-transformers` (`all-MiniLM-L6-v2`) and TF-IDF character n-gram cosine similarity to pair related skills with a $\ge 0.75$ similarity threshold.
5. **Retrieval-Augmented Generation (RAG):** Synthesizes exact matches, semantically paired skills, and remaining missing skills into a retrieved context payload, which is injected directly into the LLM prompt context to guide explainable career intelligence generation.

---

## 2. Architecture & Data Flow Diagram

```mermaid
flowchart TD
    subgraph Input Parsing
        RS["Resume Extracted Skills"]
        JDS["JD / Inferred Role Skills"]
    end

    subgraph Step 1: Exact, Variant & Alias Filter
        VAR["get_skill_variants() & check_exact_or_alias()"]
        RS --> VAR
        JDS --> VAR
        VAR -->|"Matched Skills (Score: 1.0)"| EXACT["exact_matches"]
        VAR -->|"Unmatched JD Skills"| UNMATCHED["unmatched_jd_skills"]
    end

    subgraph Step 2: Vector Embedding & Similarity Search
        EMB["SentenceTransformer('all-MiniLM-L6-v2')"]
        UNMATCHED --> EMB
        RS --> EMB
        
        VEC_RES["Resume Vector Embeddings (384-dim)"]
        VEC_JD["JD Vector Embeddings (384-dim)"]
        EMB --> VEC_RES
        EMB --> VEC_JD

        CS["compute_cosine_similarity(vec1, vec2)"]
        VEC_RES --> CS
        VEC_JD --> CS

        CS -->|"Similarity >= 0.75"| SEM["semantic_matches"]
        CS -->|"Similarity < 0.75"| MISS["still_missing_skills"]
    end

    subgraph Step 3: Retrieval-Augmented Generation (RAG)
        RAG_CTX["RAG Context Assembly"]
        EXACT --> RAG_CTX
        SEM --> RAG_CTX
        MISS --> RAG_CTX

        LLM["Groq LLM (Llama / Qwen) Career AI Engine"]
        RAG_CTX -->|"Injected Context Payload"| LLM
        LLM --> INTEL["Career Intelligence (Roadmap, Gaps, Advice)"]
    end
```

---

## 3. Mathematical & Vector Specification

### 3.1 Vector Embedding Model
* **Model:** `all-MiniLM-L6-v2` via `sentence-transformers`
* **Embedding Dimension:** $D = 384$
* **Normalized Vectors:** Outputs dense real-valued floating point vectors $\vec{v} \in \mathbb{R}^{384}$.

### 3.2 Cosine Similarity Formula
Given a JD skill embedding vector $\vec{u}$ and a candidate resume skill embedding vector $\vec{v}$, cosine similarity is calculated in [`rag_skill_matcher.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/rag_skill_matcher.py#L4-L14):

$$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} = \frac{\sum_{i=1}^{384} u_i v_i}{\sqrt{\sum_{i=1}^{384} u_i^2} \sqrt{\sum_{i=1}^{384} v_i^2}}$$

* **Threshold Filter:** Skill pairs with $\text{Similarity} \ge 0.75$ are paired as valid semantic matches (e.g. matching *"PyTorch"* to *"Deep Learning"* or *"PostgreSQL"* to *"SQL Databases"*).

---

## 4. RAG Prompt Injection Pipeline

In [`career_ai_engine.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/career_ai_engine.py#L11-L22), the vector matcher results are compiled into a retrieved context payload:

```python
RAG EMBEDDING MATCH BREAKDOWN:
- Semantically Matched Related Skills: PyTorch -> Deep Learning (Score: 0.82)
- Still Missing JD Skills: Docker, Kubernetes
```

This retrieved context is injected into the LLM system prompt:
> *"Analyze this RESUME against the JOB DESCRIPTION (or target role) and perform a comprehensive, rigorous skill gap analysis. Use the RAG EMBEDDING MATCH BREAKDOWN to ensure accurate gap identification."*

---

## 5. LangChain & Vector DB Dependencies vs Code Implementation

### Dependencies in `requirements.txt`
* `langchain>=0.1.0`
* `langchain-community>=0.0.10`
* `chromadb>=0.4.0`
* `sentence-transformers>=2.2.0`

### Code Implementation Detail
* **Direct Vector Computation:** The system utilizes `sentence-transformers` (`all-MiniLM-L6-v2`) and direct in-memory Cosine Similarity math for ultra-fast, zero-overhead execution without needing an external vector database process or heavy LangChain abstraction overhead.
* **LangChain Integration Ready:** The installed `langchain` and `chromadb` packages are available in the project environment to allow scaling up to persistent ChromaDB vector index stores or LangChain retrievers in future releases.

---

## 6. Implementation Code References

* [`resume_analyzer/services/rag_skill_matcher.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/rag_skill_matcher.py) — Core similarity search & RAG skill matching module.
* [`resume_analyzer/services/scoring_engine.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/scoring_engine.py#L33-L40) — Integration into the 4-factor ATS match score calculation.
* [`resume_analyzer/services/career_ai_engine.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/career_ai_engine.py#L7-L22) — RAG context injection into Groq LLM inference.
* [`resume_analyzer/tests/test_rag_skill_matcher.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/tests/test_rag_skill_matcher.py) — Automated test suite verifying vector similarity thresholds.
