# Product Requirement Document (PRD)

## Product Name: AI Resume Analyzer & ATS Job Matcher (ResumeIQ)
**Document Version:** 1.0 (MVP)  
**Status:** Approved for Implementation  
**Target Platform:** Django Web Application  

---

## 1. Executive Summary & Overview

The **AI Resume Analyzer & ATS Job Matcher** is a web application built on Django that empowers job seekers to optimize their job applications against automated Applicant Tracking Systems (ATS) and recruiter expectations. 

Candidates upload their resume (as a PDF document or raw text) and paste a target Job Description (JD). The system extracts structured parameters from both texts using Large Language Models (LLMs), calculates a **multi-factor hybrid ATS match score (0–100%)**, and outputs explainable, actionable career intelligence — including critical/advanced skill gaps, structural resume weaknesses, a sequential 5-step career roadmap, and strategic advice.

---

## 2. Problem Statement

Modern recruiting relies heavily on automated Applicant Tracking Systems (ATS) that parse, filter, and score candidate resumes before human recruiters inspect them. Up to **75% of candidate resumes are rejected at the ATS filtering stage** due to keyword mismatches, non-standard formatting, or unquantified achievement bullet points.

Existing public tools present critical limitations:
1. **Naive Keyword Matching:** They rely on simple substring lookups, failing to recognize semantic/related skills (e.g., recognizing that candidate experience in *PyTorch* aligns with a *Deep Learning* requirement, or *PostgreSQL* matches *Relational Databases*).
2. **Black-Box Scoring:** They output an arbitrary score without explaining *why* a candidate scored poorly or how the score was computed.
3. **Lack of Actionable Guidance:** They highlight missing keywords without providing structural resume quality audits, skill gap prioritization, or concrete upskilling roadmaps.

---

## 3. Target Users & Personas

### Persona 1: Alex - Tech Job Seeker & Career Switcher (Primary Target)
* **Background:** Software Engineer or Data Specialist applying for targeted mid-level roles.
* **Pain Points:** Submits dozens of applications weekly with low response rates; unsure if resume keywords match target JDs; lacks clear direction on which missing skills are mandatory vs. optional.
* **Goals:** Achieve 80%+ ATS match score before applying; identify exact missing technical skills; follow a structured roadmap to bridge domain knowledge gaps.

### Persona 2: Maya - Early-Career Professional & Recent Graduate (Secondary Target)
* **Background:** Entry-level candidate with strong academic projects but limited formal work history.
* **Pain Points:** Struggles to format project experience and quantify achievements for ATS parsers; receives automated rejection emails without feedback.
* **Goals:** Audit resume quality (contact info, metrics presence, project layout); optimize job alignment; receive actionable advice on highlighting academic projects.

### Persona 3: David - Mid-Senior Professional / Functional Specialist
* **Background:** Senior practitioner evaluating senior/lead postings.
* **Pain Points:** Resume contains vast historical detail; difficult to evaluate experience alignment against specific seniority requirements in target job descriptions.
* **Goals:** Quickly verify experience alignment against JD requirements; spot advanced leadership/technical skill gaps.

---

## 4. Product Goals & Non-Goals

### Product Goals
* **Goal 1 (Accuracy & Transparency):** Deliver a multi-factor hybrid score (Keyword, Semantic, Experience, Quality) with 100% explainability across all sub-scores.
* **Goal 2 (Semantic Intelligence):** Utilize NLP (TF-IDF Cosine Similarity & LLM/RAG vector matching) to evaluate conceptual and related skill alignments beyond exact text matches.
* **Goal 3 (Actionable Intelligence):** Generate structured, non-hallucinated career guidance (Critical Gaps, Advanced Gaps, Resume Quality Weaknesses, Career Roadmap, and Personalized Advice).
* **Goal 4 (Performance & Usability):** Deliver complete end-to-end analysis results within **< 5 seconds** for an average 2-page PDF resume.

### Non-Goals (Out of Scope for MVP)
* **Automated Resume Builder / PDF Generator:** Rewriting or auto-generating downloadable modified PDF resumes.
* **Live Job Posting Scraper:** Scraping external job board URLs (e.g. LinkedIn, Indeed) directly via backend web scraping.
* **Third-Party ATS API Integration:** Direct submission into Greenhouse, Lever, or Workday.
* **Employer / Recruiter Portal:** Multi-resume batch scanning for hiring managers or recruitment agencies.
* **Monetization & Payment Gateways:** Subscription billing, paywalls, or token checkout systems.

---

## 5. Core Features & Functional Requirements

```
                               ┌──────────────────────────┐
                               │ User Input (PDF / Text)  │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │ Data Ingestion & Parsing │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
                    ▼                                               ▼
     ┌─────────────────────────────┐                 ┌─────────────────────────────┐
     │  Multi-Factor ATS Scoring   │                 │ AI Career Intelligence      │
     │  (Keyword, Semantic, Exp,   │                 │ (Gaps, Roadmap, Weakness,   │
     │   Quality)                  │                 │  Advice)                    │
     └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────┐
                               │ Dashboard & History View │
                               └──────────────────────────┘
```

### Feature 1: Multi-Input Resume & Job Description Ingestion
* **Description:** Support PDF document uploads (`.pdf`) and raw text pastes for candidate resumes, alongside a plain text paste area for the target Job Description.
* **Functional Requirements:**
  * Client-side & server-side validation for file types (PDF only, max size 5MB).
  * Backend text extraction layer via `PyPDF2` with fallback error handling for corrupted files or non-readable scans.
  * Validation enforcing minimum character lengths (Resume ≥ 100 chars; JD ≥ 100 chars).

### Feature 2: LLM Structured Entity Extraction
* **Description:** Process raw unstructured resume and JD texts into standardized JSON objects using high-speed LLMs (Groq API).
* **Functional Requirements:**
  * **Extracted Resume Entity Schema:** `technical_skills`, `soft_skills`, `years_of_experience`, `education`, `projects`, `quantified_metrics_count`, `has_contact_info`.
  * **Extracted JD Entity Schema:** `job_title`, `required_skills`, `preferred_skills`, `required_experience_years`, `key_responsibilities`.
  * Automatic multi-model failover rotation (`groq/compound-mini`, `qwen/qwen3.6-27b`, `openai/gpt-oss-120b`).

### Feature 3: Multi-Factor Hybrid ATS Scoring Engine
* **Description:** Calculate an overall ATS match score (0–100%) using a deterministic, weighted multi-metric formula:
$$\text{ATS Score} = (S_{\text{keyword}} \times 0.40) + (S_{\text{semantic}} \times 0.30) + (S_{\text{experience}} \times 0.20) + (S_{\text{quality}} \times 0.10)$$

* **Sub-Metric Breakdown:**
  1. **Keyword Overlap Score ($S_{\text{keyword}}$ - 40% Weight):**
     $$\text{Overlap Ratio} = \frac{|\text{Resume Skills} \cap \text{Required JD Skills}|}{|\text{Required JD Skills}|} \times 100$$
  2. **Semantic / Related-Skill Score ($S_{\text{semantic}}$ - 30% Weight):**
     Calculates TF-IDF n-gram vector Cosine Similarity combined with LLM/RAG vector embedding context to evaluate related skills (e.g. PyTorch ~ TensorFlow).
  3. **Experience Alignment Score ($S_{\text{experience}}$ - 20% Weight):**
     Compares candidate total years of experience ($E_{\text{cand}}$) against JD requirement ($E_{\text{req}}$):
     $$S_{\text{experience}} = \min\left(100, \frac{E_{\text{cand}}}{E_{\text{req}}} \times 100\right)$$
  4. **Resume Quality Score ($S_{\text{quality}}$ - 10% Weight):**
     Evaluates resume completeness and impact:
     * Presence of quantified metrics / numbers (+30 points)
     * Documented projects (+30 points)
     * Education listing (+20 points)
     * Valid contact details (+20 points)

### Feature 4: Explainable Career Intelligence Engine
* **Description:** Transform raw metric gaps into actionable, strategic advice for candidate growth.
* **Functional Requirements:**
  * **Critical Skill Gaps:** Identify missing skills from mandatory JD requirements that significantly penalize the ATS score.
  * **Advanced Skill Gaps:** Highlight missing preferred or secondary technologies that provide competitive differentiation.
  * **Resume Weakness Audit:** Highlight structural flaws (e.g., missing metrics in bullet points, passive phrasing, missing contact links).
  * **Sequential Career Roadmap:** Generate a 5-step prioritized action plan (e.g. Step 1: Learn Missing Core Skill, Step 2: Build Hands-on Project, Step 3: Quantify Achievements).
  * **Personalized Advice:** Produce role-tailored strategic recommendations.

### Feature 5: Interactive Results Dashboard & Analysis History
* **Description:** Present scores, breakdown charts, and career intelligence in a clean UI with session history.
* **Functional Requirements:**
  * Display overall score with dynamic SVG progress gauges and color-coded status badges (High Match ≥ 75%, Moderate 50–74%, Low < 50%).
  * Provide visual pill badges for matched vs missing skills.
  * Persist analysis records to database (`ResumeAnalysis` ORM model) with full detail view retrieval at `/analysis/<id>/`.
  * Offer historical lookup page (`/history/`) displaying past analyses with timestamps and target job titles.

---

## 6. MVP Scope Definition

| Feature Area | Included in MVP | Post-MVP / Future Consideration |
| :--- | :--- | :--- |
| **Input Methods** | PDF file upload & Direct text paste for Resume & JD | DOCX support, Google Drive / Dropbox integration |
| **Parsing Engine** | PyPDF2 + Groq LLM JSON Extraction | Multi-modal OCR for image-only PDF scans |
| **Scoring Formula** | Hybrid 4-factor formula (Keyword, Semantic, Experience, Quality) | Custom candidate/recruiter customizable weights |
| **AI Intelligence** | Critical/Advanced Gaps, Weaknesses, 5-Step Roadmap, Advice | Real-time AI Resume Rewriter / Bullet Point Enhancer |
| **Persistence** | SQLite / PostgreSQL analysis log with history dashboard | User authentication (OAuth / JWT) with cloud profile storage |
| **UI / UX** | Vanilla JS glassmorphism dashboard with static asset serving | Dark/Light mode toggle, exportable PDF report download |

---

## 7. User Stories & Acceptance Criteria

### User Story 1: Resume Upload & Analysis Request (Priority: P0)
> **As a** job seeker,  
> **I want to** upload my resume as a PDF file (or paste its text) and enter a target Job Description,  
> **So that** I can evaluate my application readiness against the role requirements.

* **Acceptance Criteria:**
  1. The user interface provides a file drag-and-drop / file selector for PDF resumes and text boxes for resume/JD text.
  2. Submitting an invalid file format (non-PDF) displays a clear inline error message.
  3. Submitting text shorter than 100 characters triggers client-side validation error.
  4. Upon submission, a loading indicator is displayed while processing occurs.

### User Story 2: View Multi-Factor Match Score (Priority: P0)
> **As a** job seeker,  
> **I want to** view an overall ATS match score along with a clear sub-score breakdown,  
> **So that** I can understand exactly how my score was calculated across different criteria.

* **Acceptance Criteria:**
  1. The dashboard displays the overall ATS Score (0–100%) prominently.
  2. The system breaks down sub-scores for Keyword Match (40%), Semantic Match (30%), Experience Alignment (20%), and Resume Quality (10%).
  3. Each sub-score includes a visual progress bar or metric badge with contextual explanation.

### User Story 3: Skill Gap Identification & Career Roadmap (Priority: P0)
> **As a** job seeker,  
> **I want to** see which technical skills I am missing and get a step-by-step roadmap,  
> **So that** I can prioritize upskilling and update my resume effectively.

* **Acceptance Criteria:**
  1. Missing skills are categorized into **Critical Skill Gaps** (high priority) and **Advanced Skill Gaps** (secondary priority).
  2. Matched skills are displayed as green badges; missing skills as red/yellow badges.
  3. A 5-step sequential career roadmap is displayed with clear, actionable titles and descriptions.

### User Story 4: Historical Analysis Tracking (Priority: P1)
> **As a** job seeker,  
> **I want to** view my past resume analyses,  
> **So that** I can track how my match score improves over time across different iterations.

* **Acceptance Criteria:**
  1. The system automatically saves each completed analysis to the database.
  2. The `/history/` page lists all previous runs with job title, candidate name, date, and overall score.
  3. Clicking any history entry loads the full result dashboard for that specific analysis.

---

## 8. Success Metrics & Key Performance Indicators (KPIs)

| Metric Category | Target KPI | Measurement Method |
| :--- | :--- | :--- |
| **System Latency** | End-to-end response time **< 4.0 seconds** | Server timing logs on `/api/analyze/` endpoint |
| **Extraction Reliability** | **≥ 95%** successful extraction rate without LLM schema errors | Error log auditing of JSON parsing exceptions |
| **Score Accuracy** | **≥ 90%** correlation with manual recruiter ATS evaluation benchmarks | Internal test suite evaluation against sample resume/JD pairs |
| **User Engagement** | **≥ 60%** of visitors run 2+ analyses per session | Google Analytics / Server session tracking |
| **System Availability** | **99.5%** uptime with failover LLM routing | Infrastructure monitoring |

---

## 9. Technical Assumptions & Environment Dependencies

1. **Backend Infrastructure:** Python 3.10+, Django 4.2 LTS framework, Django REST Framework.
2. **Database:** SQLite for local development; PostgreSQL (Supabase / Managed Postgres) for production deployment via `dj-database-url`.
3. **LLM Inference Provider:** Groq Cloud API access with active API keys configured in `.env`.
4. **Python Dependencies:** `PyPDF2` (PDF text extraction), `scikit-learn` (TF-IDF vectorization & Cosine Similarity), `python-dotenv` (secrets management), `whitenoise` (static asset delivery).
5. **Browser Support:** Modern web browsers (Chrome 100+, Firefox 100+, Edge, Safari 15+) with JavaScript enabled.

---

## 10. Risks & Mitigation Strategies

| Identified Risk | Severity | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Groq API Rate Limits / Outage** | High | LLM extraction and career intelligence generation fails. | Implement multi-model failover rotation (`groq/compound-mini`, `qwen/qwen3.6-27b`, `openai/gpt-oss-120b`) and fallback rule-based skill extraction (`skill_extractor.py`). |
| **Unparseable / Image-based PDFs** | Medium | PyPDF2 returns empty text string for scanned image PDFs. | Validate extracted text length immediately after extraction; display helpful error asking user to paste raw text if PDF text layer is empty. |
| **LLM Schema Misalignment / Hallucinations** | Medium | LLM returns non-JSON or invalid fields. | Use strict Pydantic / JSON schema constraints and fallback regex parsing to enforce valid JSON structures. |
| **TF-IDF Keyword Noise** | Low | High frequency stop-words distorting cosine similarity. | Apply custom stop-word removal and n-gram ranges (1, 2) tuned specifically for technical resume vocabulary. |

---

## 11. Out-of-Scope & Future Enhancements (Roadmap)

* **Phase 2 (Post-MVP):**
  * Automated Resume Bullet-Point Generator (AI-suggested improvements for resume bullet points).
  * Direct `.docx` file support.
  * PDF report download export button for offline viewing.
* **Phase 3 (Enterprise & Scalability):**
  * OAuth2 social login (Google, GitHub, LinkedIn).
  * Recruiter mode allowing bulk PDF upload to rank candidates against a single JD.
  * Direct integration with job board APIs for 1-click job match checking.

---

## 12. Acceptance Criteria & Definition of Done (DoD)

To consider the MVP feature complete and ready for release, all of the following conditions must be satisfied:
* [x] **End-to-End Flow Validation:** A user can upload a PDF resume, paste a JD, click analyze, and view complete results without backend errors.
* [x] **Scoring Accuracy:** The 4-part hybrid score formula operates deterministically and sums accurately to 100%.
* [x] **Career Intelligence Completeness:** Results render all five intelligence elements: Critical Gaps, Advanced Gaps, Resume Weaknesses, 5-Step Career Roadmap, and Personalized Advice.
* [x] **Database Persistence:** Every analysis creates a valid `ResumeAnalysis` DB entry accessible via `/analysis/<id>/` and listed on `/history/`.
* [x] **Performance Benchmark:** Page analysis completes in under 5 seconds under standard network conditions.
* [x] **Documentation Alignment:** Codebase matches `ARCHITECTURE.md` and `README.md` system definitions.
