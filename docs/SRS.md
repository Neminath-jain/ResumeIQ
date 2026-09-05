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
  $$\text{ATS Score} = (S_{\text{keyword}} \times 0.35) + (S_{\text{semantic}} \times 0.35) + (S_{\text{experience}} \times 0.15) + (S_{\text{quality}} \times 0.15)$$
  All sub-scores and overall scores MUST be bounded between $0.0\%$ and $100.0\%$.

* **BR-002 (Skill Matching Hierarchy & Variant Decomposition):**
  * **Exact & Alias Match ($S_{\text{keyword}}$):** Case-insensitive string matching, bidirectional technology alias mapping (`TECH_ALIASES`), and compound skill decomposition (`get_skill_variants`) to unpack parenthesized skills (e.g. `SQL (PostgreSQL, MySQL)` $\rightarrow$ `sql`, `postgresql`, `mysql`) and alternatives (`TensorFlow or PyTorch`).
  * **Semantic Match ($S_{\text{semantic}}$):** Dense vector embedding / Cosine Similarity via SentenceTransformers (`all-MiniLM-L6-v2`) combined with TF-IDF character n-gram cosine similarity.

* **BR-003 (Experience Alignment Cap):**
  * Candidate experience ($E_{\text{cand}}$) meeting or exceeding requested experience ($E_{\text{req}}$) yields $100\%$.
  * If $E_{\text{req}} > 0$ and $E_{\text{cand}} < E_{\text{req}}$, score is pro-rated according to tier brackets ($80\%$ if 1 year below, $60\%$ if 2 years below, $40\%$ otherwise).
  * If $E_{\text{req}} = 0$, default $S_{\text{experience}} = 75\%$ (or $60\%$ if candidate experience is unstated).

* **BR-004 (Resume Quality Scoring Allocation):**
  * Base score: $40\%$
  * Quantified achievements listed: up to $+30\%$
  * Projects documented: up to $+15\%$
  * Education verified: $+10\%$
  * Metrics/numbers present in bullet points: up to $+15\%$ (capped at $100\%$).

* **BR-005 (Data Retention & Storage):** Analysis results MUST be persisted in PostgreSQL (production via Supabase) or local SQLite, associated with the active candidate's account.

---

## 4. Functional Requirements (FR)

### 4.1 Ingestion & Parsing Module
* **FR-ING-001:** The system SHALL accept PDF uploads (`.pdf`) up to 5MB in file size.
* **FR-ING-002:** The system SHALL extract raw text from PDF files using `PyPDF2` binary text extraction.
* **FR-ING-003:** The system SHALL provide a fallback plain text textarea allowing users to paste resume text directly.
* **FR-ING-004:** The system SHALL accept either a multi-paragraph job description OR a short target role title (e.g. *"Full Stack Engineer"*, *"AI Developer"*, *"Data Analyst"*).

### 4.2 LLM Entity Extraction & Role Inference Module
* **FR-EXT-001:** The system SHALL send cleaned resume and JD text to the Groq API for structured JSON extraction.
* **FR-EXT-002:** The LLM extraction payload SHALL return standard JSON matching the target schema (`technical_skills`, `years_experience`, `education`, `projects`, `quantified_achievements`).
* **FR-EXT-003:** If the user inputs a short role title/summary, the system SHALL automatically infer 8–12 standard industry-required technical skills, preferred skills, and experience requirements to prevent empty-skill evaluation.
* **FR-EXT-004:** If all LLM calls fail or timeout, the system SHALL execute the rule-based fallback skill extractor (`skill_extractor.py`) using its 300+ technical skill catalog and role-to-skills template mapping.

### 4.3 Hybrid RAG & ATS Scoring Module
* **FR-SCR-001:** The system SHALL calculate $S_{\text{keyword}}$ by checking exact matches, aliases, and decomposed skill variants against resume skills and raw resume text.
* **FR-SCR-002:** The system SHALL calculate $S_{\text{semantic}}$ by generating vector embeddings (`SentenceTransformer('all-MiniLM-L6-v2')`) and computing Cosine Similarity between vector arrays in `rag_skill_matcher.py`.
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
* **FR-UI-003:** The system SHALL save every analysis event to the `ResumeAnalysis` model and provide a permanent retrieval endpoint at `/result/<id>/`.
* **FR-UI-004:** The system SHALL provide a `/history/` dashboard displaying a tabular summary of past analyses with date, candidate role, status, and score.
* **FR-UI-005:** The system SHALL connect to Supabase PostgreSQL database via `DATABASE_URL` with SSL support and connection pooling.

---

## 5. Data Requirements & Database Schema

### 5.1 Database Entity: `ResumeAnalysis` (`resume_analyzer_resumeanalysis`)

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `BigAutoField` | Primary Key, Auto Increment | Unique analysis identifier. |
| `user_id` | `ForeignKey` | FK $\rightarrow$ `auth_user.id`, CASCADE | Owner of the analysis record. |
| `resume_file` | `FileField` | Upload path `resumes/`, Nullable | Uploaded PDF binary file path. |
| `resume_text` | `TextField` | Blank Allowed | Extracted/pasted raw resume text. |
| `job_description` | `TextField` | NOT NULL | Target job description text. |
| `status` | `CharField(20)` | Choices: `pending`, `processing`, `completed`, `failed` | Workflow status. |
| `ats_score` | `FloatField` | Nullable, $0.0 \le x \le 100.0$ | Overall weighted ATS match score. |
| `keyword_score` | `FloatField` | Nullable, $0.0 \le x \le 100.0$ | Sub-score: Keyword overlap. |
| `semantic_score` | `FloatField` | Nullable, $0.0 \le x \le 100.0$ | Sub-score: Semantic similarity. |
| `experience_score` | `FloatField` | Nullable, $0.0 \le x \le 100.0$ | Sub-score: Experience alignment. |
| `quality_score` | `FloatField` | Nullable, $0.0 \le x \le 100.0$ | Sub-score: Resume structural quality. |
| `detected_role` | `CharField(200)`| Blank Allowed | Role detected by LLM. |
| `experience_level` | `CharField(100)`| Blank Allowed | Seniority level detected. |
| `critical_skill_gaps_json` | `TextField` | Default `[]` | JSON array of missing critical skills. |
| `advanced_skill_gaps_json` | `TextField` | Default `[]` | JSON array of missing advanced skills. |
| `resume_weaknesses_json` | `TextField` | Default `[]` | JSON array of detected weaknesses. |
| `career_roadmap_json` | `TextField` | Default `[]` | JSON array of 5-step roadmap items. |
| `personalized_advice` | `TextField` | Blank Allowed | Strategic recommendations text. |
| `skill_match_breakdown_json`| `TextField` | Default `{}` | JSON map of exact/semantic skill matches. |
| `created_at` | `DateTimeField` | Auto Now Add | Timestamp of analysis creation. |
| `updated_at` | `DateTimeField` | Auto Now | Timestamp of last modification. |

---

## 6. Input Validations & Sanitization

| Field / Parameter | Validation Rule | Error Action |
| :--- | :--- | :--- |
| `resume_file` | File extension MUST be `.pdf`. File size MUST be $\le 5\text{MB}$. | Reject submission with HTTP 400: *"Invalid file type or file exceeds 5MB limit."* |
| `resume_text` | Minimum length $\ge 100$ characters after whitespace trimming. | Reject submission with HTTP 400: *"Resume text too short."* |
| `job_description` | Minimum length $\ge 100$ characters after whitespace trimming. | Reject submission with HTTP 400: *"Job Description text too short."* |
| Input Text Sanitization | Strip HTML tags, script elements, and invalid UTF-8 byte sequences. | Sanitize input before processing. |

---

## 7. Authentication, Authorization & Security

### 7.1 Authentication & Session Management
* Web UI uses Django standard session authentication with secure HTTP-only session cookies.
* API endpoints (`/api/analyze/`) require active user session or DRF Token Header (`Authorization: Token <key>`).

### 7.2 Security Requirements (SEC)
* **SEC-001 (Secret Protection):** All sensitive keys (`GROQ_API_KEY`, `SECRET_KEY`, `DATABASE_URL`) MUST be loaded strictly via environment variables using `python-dotenv`.
* **SEC-002 (CSRF Defense):** All state-changing HTML form submissions MUST include valid Django CSRF tokens (`{% csrf_token %}`).
* **SEC-003 (File Security):** Uploaded PDF files MUST be stored in dedicated media directories (`/media/resumes/`) with executable flags disabled.
* **SEC-004 (SQL Injection & XSS Defense):** Queries MUST use Django ORM parameterized statements; UI outputs MUST escape HTML entities.

---

## 8. Error Handling & Edge Cases

| Scenario / Edge Case | System Behavior & Mitigation |
| :--- | :--- |
| **Scanned Image PDF (No Text Layer)** | `PyPDF2` returns empty text string. System detects `len(text) < 100` and displays inline alert: *"Scanned PDF detected without text layer. Please paste raw resume text."* |
| **Groq API Rate Limit (HTTP 429)** | System catches rate limit exception, logs warning, automatically rotates to secondary LLM model, or invokes rule-based extractor fallback. |
| **Malformed LLM JSON Response** | Regex parser extracts valid JSON substring; if parsing fails completely, system populates default structured fallbacks. |
| **Missing DB Connection** | System catches database exception and returns HTTP 503 with user-friendly retry message. |

---

## 9. Performance & Non-Functional Requirements (NFR)

* **NFR-PERF-001 (Response Time):** Analysis endpoint `/api/analyze/` MUST return complete JSON response within **< 4.0 seconds** for standard resumes.
* **NFR-RELI-002 (Availability):** System MUST achieve **99.5% uptime** excluding scheduled maintenance windows.
* **NFR-SCAL-003 (Concurrency):** System backend SHALL support at least 50 concurrent analysis requests without memory overflow.
* **NFR-COMP-004 (Browser Compatibility):** Web templates MUST render accurately on Chrome, Firefox, Edge, and Safari (desktop & mobile viewpoints).

---

## 10. Acceptance Criteria & Test Matrix

```
  Test Case ID    Requirement ID     Test Scenario                        Expected Result
 ──────────────  ────────────────  ───────────────────────────────────  ────────────────────────────────────
  TC-ING-01       FR-ING-001        Upload 6MB PDF file                  HTTP 400 Validation Error returned
  TC-ING-02       FR-ING-002        Upload standard 2-page PDF           Text successfully extracted
  TC-SCR-01       FR-SCR-001        Resume skills match 4 of 5 JD skills Keyword score = 80.0%
  TC-SCR-02       BR-001            Verify hybrid ATS formula            Overall score equals weighted sum
  TC-INT-01       FR-INT-001        Verify skill gap categorization      Gaps split into Critical & Advanced
  TC-ERR-01       SEC-001           Simulate Groq API timeout            Auto-failover to secondary model
```

### Detailed Verification Criteria:
1. **TC-ING-01:** Verifies file size limit enforcement at 5MB.
2. **TC-ING-02:** Verifies text layer extraction via `PyPDF2`.
3. **TC-SCR-01:** Verifies exact keyword score calculation accuracy ($4/5 = 80\%$).
4. **TC-SCR-02:** Verifies overall score matches $(40\% \cdot S_{\text{kw}}) + (30\% \cdot S_{\text{sem}}) + (20\% \cdot S_{\text{exp}}) + (10\% \cdot S_{\text{qual}})$.
5. **TC-INT-01:** Verifies JSON payload structures for critical vs advanced skill gaps.
6. **TC-ERR-01:** Verifies failover mechanism when primary Groq model fails.
