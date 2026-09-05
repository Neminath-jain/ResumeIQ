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

### Feature 1: Multi-Input Resume & Job Description / Target Role Ingestion
* **Description:** Support PDF document uploads (`.pdf`) and raw text pastes for candidate resumes, alongside a flexible text area for either a complete target Job Description OR a short Target Role name (e.g. *"Full Stack Engineer"*, *"AI Developer"*, *"Data Analyst"*).
* **Functional Requirements:**
  * Client-side & server-side validation for file types (PDF only, max size 5MB).
  * Backend text extraction layer via `PyPDF2` with fallback error handling for corrupted files or non-readable scans.
  * Validation enforcing minimum character lengths for resume text.

### Feature 2: LLM Structured Entity Extraction & Role Inference
* **Description:** Process raw unstructured resume and JD texts into standardized JSON objects using high-speed LLMs (Groq API), with automatic role skill inference and offline fallback.
* **Functional Requirements:**
  * **Extracted Resume Entity Schema:** `technical_skills`, `years_experience`, `education`, `projects`, `quantified_achievements`.
  * **Extracted JD / Role Entity Schema:** `required_skills`, `preferred_skills`, `experience_required`.
  * **Role Inference:** When a target role title is provided, automatically infers 8–12 standard industry-required skills, preferred skills, and experience benchmarks.
  * **Multi-Layer Resilience:** Rule-based fallback skill extractor (`skill_extractor.py`) with 300+ skills catalog and role templates.

### Feature 3: Multi-Factor Hybrid ATS Scoring Engine
* **Description:** Calculate an overall ATS match score (0–100%) using a deterministic, weighted multi-metric formula:
$$\text{ATS Score} = (S_{\text{keyword}} \times 0.35) + (S_{\text{semantic}} \times 0.35) + (S_{\text{experience}} \times 0.15) + (S_{\text{quality}} \times 0.15)$$

* **Sub-Metric Breakdown:**
  1. **Keyword Overlap Score ($S_{\text{keyword}}$ - 35% Weight):**
     Matches exact skills, aliases (`TECH_ALIASES`), and decomposed variants (`get_skill_variants`) against resume skills and raw resume text.
  2. **Semantic / Related-Skill Score ($S_{\text{semantic}}$ - 35% Weight):**
     Calculates SentenceTransformer dense vector Cosine Similarity combined with TF-IDF character n-gram cosine similarity (threshold $\ge 0.75$).
  3. **Experience Alignment Score ($S_{\text{experience}}$ - 15% Weight):**
     Compares candidate total years of experience against JD / role requirements using tiered brackets.
  4. **Resume Quality Score ($S_{\text{quality}}$ - 15% Weight):**
     Evaluates resume completeness and impact (base 40 points, quantified achievements up to +30, projects up to +15, education +10, numbers/metrics in bullets up to +15).

### Feature 4: Explainable Career Intelligence Engine
* **Description:** Transform raw metric gaps into actionable, strategic advice for candidate growth.
* **Functional Requirements:**
  * **Critical Skill Gaps:** Identify missing skills from mandatory JD requirements that significantly penalize the ATS score.
  * **Advanced Skill Gaps:** Highlight missing preferred or secondary technologies that provide competitive differentiation.
  * **Resume Weakness Audit:** Highlight structural flaws (e.g., missing metrics in bullet points, passive phrasing, missing links).
  * **Sequential Career Roadmap:** Generate a 5-step prioritized action plan.
  * **Personalized Advice:** Produce role-tailored strategic recommendations.

### Feature 5: Interactive Results Dashboard & Analysis History
* **Description:** Present scores, breakdown charts, and career intelligence in a clean UI with session history.
* **Functional Requirements:**
  * Display overall score with dynamic SVG progress gauges and color-coded status badges.
  * Provide visual pill badges for matched vs missing skills.
  * Persist analysis records to database (`ResumeAnalysis` ORM model, supporting Supabase PostgreSQL and SQLite) with full detail view retrieval at `/result/<id>/`.
  * Offer historical lookup page (`/history/`) displaying past analyses with timestamps, target roles, status, and scores.
