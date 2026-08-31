# Software Requirements Specification (SRS)

## Product Name: AI Resume Analyzer & ATS Job Matcher (ResumeIQ)
**Document Version:** 1.0  
**Status:** Approved for Implementation  
**Target Framework:** Django 4.2 LTS / Django REST Framework  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the complete functional, non-functional, data, security, and interface requirements for the **AI Resume Analyzer & ATS Job Matcher**. It serves as the single source of truth for software engineers, QA testers, system architects, and project stakeholders.

### 1.2 Scope
The application is a web-based intelligence platform designed to extract structured information from candidate resumes (PDF or raw text) and job descriptions (plain text), compute a deterministic multi-factor match score (Keyword, Semantic/RAG Skill, Experience, Quality), and synthesize explainable career intelligence (Critical/Advanced skill gaps, structural weaknesses, a 5-step career roadmap, and personalized advice).

---

## 2. User Roles & Permissions

The system enforces Role-Based Access Control (RBAC) across two distinct primary roles:

| Role ID | Role Name | System Permissions & Access Scope |
| :--- | :--- | :--- |
| **ROLE-01** | **Candidate / Job Seeker** | - Submit resume (PDF upload / direct text paste) and target Job Description.<br>- View real-time ATS match scores and career intelligence breakdowns.<br>- Access personal historical resume analysis logs (`/history/`).<br>- Delete or re-analyze past entries owned by their user ID. |
| **ROLE-02** | **System Administrator** | - Access Django Admin portal (`/admin/`).<br>- View system-wide usage metrics, model performance, and error logs.<br>- Manage user accounts, database backups, and API integration settings (`GROQ_API_KEY`). |

---

## 3. Business Rules (BR)

* **BR-001 (Deterministic Hybrid Scoring):** The overall ATS Match Score MUST be calculated using the strict formula:
  $$\text{ATS Score} = (S_{\text{keyword}} \times 0.40) + (S_{\text{semantic}} \times 0.30) + (S_{\text{experience}} \times 0.20) + (S_{\text{quality}} \times 0.10)$$
  All sub-scores and overall scores MUST be bounded between $0.0\%$ and $100.0\%$.

* **BR-002 (Skill Matching Hierarchy):**
  * **Exact Match ($S_{\text{keyword}}$):** Direct case-insensitive string intersection between extracted candidate skills and mandatory job skills.
  * **Semantic Match ($S_{\text{semantic}}$):** Dense vector embedding / Cosine Similarity via SentenceTransformers (`all-MiniLM-L6-v2`) evaluating equivalent technologies (e.g. *PostgreSQL* $\approx$ *SQL*, *PyTorch* $\approx$ *Deep Learning*).

* **BR-003 (Experience Alignment Cap):**
  * Candidate experience ($E_{\text{cand}}$) meeting or exceeding requested experience ($E_{\text{req}}$) yields $100\%$.
  * If $E_{\text{req}} > 0$ and $E_{\text{cand}} < E_{\text{req}}$, score is pro-rated: $S_{\text{experience}} = \frac{E_{\text{cand}}}{E_{\text{req}}} \times 100$.
  * If $E_{\text{req}} = 0$, default $S_{\text{experience}} = 100\%$.

* **BR-004 (Resume Quality Scoring Allocation):**
  * Quantified Metrics/Numbers present in bullets: $+30\%$
  * Projects listed: $+30\%$
  * Education listed: $+20\%$
  * Valid contact details (Email/Phone/LinkedIn): $+20\%$

* **BR-005 (Data Retention):** Analysis results MUST be persisted in the database associated with the active candidate's account until explicitly deleted by the user or purged after 365 days of user inactivity.

---

## 4. Functional Requirements (FR)

### 4.1 Ingestion & Parsing Module
* **FR-ING-001:** The system SHALL accept PDF uploads (`.pdf`) up to 5MB in file size.
* **FR-ING-002:** The system SHALL extract raw text from PDF files using `PyPDF2` binary text extraction.
* **FR-ING-003:** The system SHALL provide a fallback plain text textarea allowing users to paste resume text directly.
* **FR-ING-004:** The system SHALL enforce a minimum character threshold of 100 characters for both the resume and the target job description.

### 4.2 LLM Entity Extraction Module
* **FR-EXT-001:** The system SHALL send cleaned resume and JD text to the Groq API for structured JSON extraction.
* **FR-EXT-002:** The LLM extraction payload SHALL return standard JSON matching the target schema (`technical_skills`, `soft_skills`, `years_of_experience`, `education`, `projects`, `metrics_count`, `has_contact`).
* **FR-EXT-003:** In the event of Groq API rate limits or timeout errors, the system SHALL execute automated failover across pre-configured models (`groq/compound-mini` $\rightarrow$ `qwen/qwen3.6-27b` $\rightarrow$ `openai/gpt-oss-120b`).
* **FR-EXT-004:** If all LLM calls fail, the system SHALL execute a rule-based fallback skill extractor (`skill_extractor.py`) to prevent service disruption.

### 4.3 Hybrid RAG & ATS Scoring Module
* **FR-SCR-001:** The system SHALL calculate $S_{\text{keyword}}$ by computing exact skill intersections against JD mandatory skills.
* **FR-SCR-002:** The system SHALL calculate $S_{\text{semantic}}$ by generating 384-dim vector embeddings (`SentenceTransformer('all-MiniLM-L6-v2')`) and computing Cosine Similarity between vector arrays in `rag_skill_matcher.py`.
* **FR-SCR-003:** The system SHALL compute $S_{\text{experience}}$ and $S_{\text{quality}}$ according to business rules **BR-003** and **BR-004**.
* **FR-SCR-004:** The system SHALL aggregate all weighted sub-scores into an overall float `ats_score` rounded to 1 decimal place.

### 4.4 AI Career Intelligence Engine
* **FR-INT-001:** The system SHALL classify missing skills into **Critical Skill Gaps** (high severity impact on hiring decision) and **Advanced Skill Gaps** (nice-to-have domain additions).
* **FR-INT-002:** The system SHALL analyze candidate text for structural flaws (e.g. passive language, lack of metrics, missing links) and output a list of **Resume Weaknesses**.
* **FR-INT-003:** The system SHALL synthesize a 5-step sequential **Career Roadmap** specifying actionable steps to bridge identified skill gaps.
* **FR-INT-004:** The system SHALL generate **Personalized Strategic Advice** tailored specifically to the target job title.

### 4.5 Persistence & User Interface Module
* **FR-UI-001:** The system SHALL display overall ATS Match Score using dynamic SVG progress rings and color-coded status pills (Green $\ge 75\%$, Yellow $50\text{--}74\%$, Red $< 50\%$).
* **FR-UI-002:** The system SHALL render skill match status using visual pill badges (Green for matched, Red for missing).
* **FR-UI-003:** The system SHALL save every analysis event to the `ResumeAnalysis` model and provide a permanent retrieval endpoint at `/analysis/<id>/`.
* **FR-UI-004:** The system SHALL provide a `/history/` dashboard displaying a tabular summary of past analyses with date, candidate name, job title, and score.
