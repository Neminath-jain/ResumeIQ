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
* **Goal 1 (Accuracy & Transparency):** Deliver a multi-factor hybrid score (Keyword, Semantic/RAG, Experience, Quality) with 100% explainability across all sub-scores.
* **Goal 2 (Semantic Intelligence):** Utilize NLP (SentenceTransformers vector similarity & LLM/RAG embedding matching) to evaluate conceptual and related skill alignments beyond exact text matches.
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
     │  (Keyword, RAG Semantic,   │                 │ (Gaps, Roadmap, Weakness,   │
     │   Experience, Quality)      │                 │  Advice)                    │
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
     Calculates SentenceTransformer dense vector Cosine Similarity combined with RAG vector embedding context to evaluate related skills (e.g. PyTorch ~ TensorFlow).
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
  * **Sequential Career Roadmap:** Generate a 5-step prioritized action plan.
  * **Personalized Advice:** Produce role-tailored strategic recommendations.

### Feature 5: Interactive Results Dashboard & Analysis History
* **Description:** Present scores, breakdown charts, and career intelligence in a clean UI with session history.
* **Functional Requirements:**
  * Display overall score with dynamic SVG progress gauges and color-coded status badges.
  * Provide visual pill badges for matched vs missing skills.
  * Persist analysis records to database (`ResumeAnalysis` ORM model) with full detail view retrieval at `/analysis/<id>/`.
  * Offer historical lookup page (`/history/`) displaying past analyses with timestamps and target job titles.
