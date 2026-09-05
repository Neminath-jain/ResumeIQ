# System Architecture Document

## Product Name: AI Resume Analyzer & ATS Job Matcher (ResumeIQ)
**Document Version:** 1.0  
**Status:** Approved Architectural Blueprint  
**Primary Framework:** Django 4.2 LTS / Groq LLM Acceleration / Sentence Transformers RAG / scikit-learn NLP  

---

## 1. Executive Architecture Summary

The **AI Resume Analyzer & ATS Job Matcher** is a web-based artificial intelligence platform designed to parse candidate resumes, compare them against target job descriptions, calculate a 4-factor ATS match score (Keyword, Semantic/RAG, Experience, Quality), and synthesize explainable career intelligence.

The architecture emphasizes **practicality, transparency, and high performance** — using a monolithic Django application with modular service layers, fast in-memory Sentence Transformer vector embeddings, vector cosine similarity matching, external high-speed LLM inference (Groq API), and persistent ORM storage.

---

## 2. Tech Stack Selection & Justification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FULL TECH STACK                                 │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ Layer             │ Technologies Chosen                                     │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Frontend UI       │ HTML5, Vanilla JavaScript (ES6+), Modern CSS3 (Glass)   │
│ Backend Web App   │ Python 3.10+, Django 4.2 LTS, Django REST Framework     │
│ AI / LLM Engine   │ Groq API (Llama 3.3 70B, Qwen 3.6 27B, Compound Mini)   │
│ RAG & Vector NLP  │ SentenceTransformers (all-MiniLM-L6-v2), Cosine Sim   │
│ Legacy Semantic   │ scikit-learn (TF-IDF Vectorizer & Cosine Similarity)    │
│ Framework/Orch    │ LangChain & ChromaDB (Dependencies ready for scale)     │
│ PDF Extraction    │ PyPDF2 (Binary text layer parser)                       │
│ Data Persistence  │ PostgreSQL (Production via Supabase) / SQLite (Local)  │
│ Asset Delivery    │ WhiteNoise (Static file middleware)                     │
│ Server / Gateway  │ Gunicorn / Uvicorn (WSGI/ASGI application server)       │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 3. High-Level System Architecture & Component Diagram

```mermaid
flowchart TD
    subgraph Client Layer
        U["Browser / User Interface (Vanilla JS + Glassmorphism)"]
    end

    subgraph API & Routing Layer
        R["Django Request Router / Middleware (urls.py)"]
        V["REST API View (AnalyzeResumeView)"]
        R --> V
    end

    subgraph Business Logic & Service Layer
        P["PDF Text Extractor (pdf_extractor.py)"]
        L["Groq LLM Structured Extractor (llm_service.py)"]
        RAG["RAG / Embedding Skill Matcher (rag_skill_matcher.py)"]
        S["Hybrid ATS Scoring Engine (scoring_engine.py)"]
        C["AI Career Intelligence Engine (career_ai_engine.py)"]
    end

    subgraph Persistence Layer
        DB[("PostgreSQL / SQLite Database (ResumeAnalysis)")]
        FS["Local / Cloud Storage (Uploaded PDF Files)"]
    end

    subgraph External Services
        GROQ["Groq Cloud LLM API (Groq Llama / Qwen Models)"]
    end

    U -->|"POST /api/analyze/ (PDF/Text + JD)"| R
    V --> P
    V --> L
    L -->|"HTTP POST JSON Schema"| GROQ
    GROQ -->|"Extracted Structured JSON"| L
    
    L --> RAG
    L --> S
    RAG --> S
    RAG --> C
    
    S -->|"Sub-scores (Keyword, Semantic, Exp, Quality)"| V
    C -->|"Gaps, Roadmap, Weakness, Advice"| V
    
    V -->|"Save Analysis Record"| DB
    V -->|"Save PDF File"| FS
    V -->|"JSON Response with ID"| U
```

---

## 4. Subsystem Components & Responsibilities

### 4.1 Ingestion & Parsing Subsystem ([`pdf_extractor.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/pdf_extractor.py))
* **Responsibility:** Ingest binary PDF files or raw text input.
* **Mechanism:** Utilizes `PyPDF2.PdfReader` to extract clean text streams, handles empty pages, strips control characters, and performs minimum character length checks ($\ge 100$ chars).

### 4.2 LLM Entity Extraction Subsystem ([`llm_service.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/llm_service.py))
* **Responsibility:** Convert unstructured resume text and JD text into strongly typed JSON structures.
* **Mechanism:** 
  * Formulates prompt templates enforcing JSON output with atomic skill breakdown.
  * **Role Inference:** If the user inputs a short job title/role (e.g. *"Full Stack Engineer"*, *"AI Developer"*, *"Data Analyst"*), the parser automatically infers 8–12 standard industry-required skills, preferred skills, and expected experience.
  * Features multi-model failover rotation across Groq models and resilient fallback to `skill_extractor.py`.

### 4.3 RAG & Embedding Skill Matcher Subsystem ([`rag_skill_matcher.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/rag_skill_matcher.py))
* **Responsibility:** Vector embedding generation, compound skill decomposition, and cosine similarity matching.
* **Mechanism:** 
  * **Variant Decomposition (`get_skill_variants`):** Decomposes compound skills, parentheses, and conjunctions (e.g., `SQL (PostgreSQL, MySQL)` $\rightarrow$ `sql`, `postgresql`, `mysql`; `TensorFlow or PyTorch` $\rightarrow$ `tensorflow`, `pytorch`).
  * **Technology Aliases:** Expanded bidirectional dictionary (`TECH_ALIASES`) mapping synonyms (React, Node, Postgres, Kubernetes, Golang, AWS, GCP, CI/CD, Vector DBs).
  * Generates dense 384-dimensional vectors via `SentenceTransformer('all-MiniLM-L6-v2')` and computes cosine similarity with a $\ge 0.75$ threshold filter.

### 4.4 Hybrid ATS Scoring Subsystem ([`scoring_engine.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/scoring_engine.py))
* **Responsibility:** Calculate the 4-factor weighted ATS score.
* **Formulas:**
  $$\text{ATS Score} = (S_{\text{keyword}} \times 0.35) + (S_{\text{semantic}} \times 0.35) + (S_{\text{experience}} \times 0.15) + (S_{\text{quality}} \times 0.15)$$
  1. **Keyword Match ($S_{\text{keyword}}$ - 35%):** Exact and alias skill set intersection including variant matching against full resume text.
  2. **Semantic Similarity / RAG ($S_{\text{semantic}}$ - 35%):** Dense vector embedding similarity match score combined with TF-IDF character n-gram cosine similarity.
  3. **Experience Score ($S_{\text{experience}}$ - 15%):** Evaluates candidate years of experience against target requirements.
  4. **Quality Score ($S_{\text{quality}}$ - 15%):** Audits quantified achievements, projects, education, and metrics in bullet points.

### 4.5 AI Career Intelligence Subsystem ([`career_ai_engine.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/career_ai_engine.py))
* **Responsibility:** Generate explainable feedback components with RAG context injection (Critical Gaps, Advanced Gaps, Resume Weaknesses, Career Roadmap, and Strategic Advice).

### 4.6 Rule-Based Fallback Skill Extractor ([`skill_extractor.py`](file:///c:/Users/parshwanath/OneDrive/Documents/GITHUB-PROJECTS/ai_resume_analyzer/resume_analyzer/services/skill_extractor.py))
* **Responsibility:** Offline and zero-downtime fallback skill extraction.
* **Mechanism:** Maintains a comprehensive catalog of 300+ technical skills (languages, frameworks, databases, cloud, DevOps, AI/ML, testing) and role-to-skills template mapping using word-boundary regex matching.

---

## 5. End-to-End Data Flow Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate Browser
    participant API as Django API View
    participant PDF as PyPDF2 Service
    participant LLM as Groq LLM Client
    participant RAG as RAG Skill Matcher
    participant Scorer as Hybrid Scoring Engine
    participant Career as Career AI Engine
    participant DB as Database (ORM)

    User->>API: POST /api/analyze/ (PDF file or Text + Job Description)
    alt PDF file uploaded
        API->>PDF: extract_text_from_pdf(file)
        PDF-->>API: Clean Raw Resume Text
    end
    
    API->>LLM: extract_structured_resume(resume_text)
    LLM-->>API: Resume Structured JSON
    
    API->>LLM: extract_structured_jd(jd_text)
    LLM-->>API: JD Structured JSON

    API->>RAG: match_skills_rag(resume_skills, required_skills)
    RAG-->>API: RAG Match Object (Exact, Semantic, Missing)
    
    API->>Scorer: compute_ats_score(resume_json, jd_json)
    Scorer-->>API: Sub-scores & Overall ATS Score
    
    API->>Career: generate_career_intelligence(resume_json, jd_json, rag_match)
    Career-->>API: Gaps, Weaknesses, Roadmap & Advice
    
    API->>DB: ResumeAnalysis.objects.create(...)
    DB-->>API: Saved Record (ID #102)
    
    API-->>User: HTTP 200 OK JSON { status: "success", analysis_id: 102 }
    User->>API: GET /analysis/102/
    API-->>User: Rendered Dashboard HTML (result.html)
```
