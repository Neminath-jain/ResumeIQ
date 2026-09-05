# AI Resume Analyzer & ATS-Based Job Matcher
### Django + Groq (Llama 3 - FREE) | Hybrid ATS Scoring Engine

---

## 📚 Project Documentation

Detailed system architecture and specifications are available in the [`docs/`](docs/README.md) folder:
* 🏗️ [**Architecture Guide**](docs/ARCHITECTURE.md)
* 🧠 [**RAG & Similarity Search Specification**](docs/RAG_AND_SIMILARITY_SEARCH.md)
* 📋 [**Product Requirements (PRD)**](docs/PRD.md)
* ⚙️ [**Software Requirements (SRS)**](docs/SRS.md)
* 🎨 [**UI/UX Specification**](docs/UI_UX.md)
* 🤖 [**AI Chatbot Setup Guide**](docs/CHATBOT_SETUP.md)

---

## Quick Start

### 1. Extract and enter the project
```bash
cd ai_resume_analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
.\myenv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get your FREE Groq API key
- Go to **https://console.groq.com**
- Sign up (no credit card needed)
- Create an API key (takes 1 minute)
- Free limits: **14,400 requests/day, 500,000 tokens/day**

### 5. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and add:
```
GROQ_API_KEY=gsk_your_key_here
```

### 6. (Optional) Connect to Supabase PostgreSQL
By default, the app runs on local SQLite. To connect to a cloud Supabase database:
1. In Supabase Dashboard $\rightarrow$ **Project Settings** $\rightarrow$ **Database** $\rightarrow$ **Connection string (URI)**.
2. Select **Session mode (Port 5432)** (recommended for Django migrations).
3. Add to `.env`:
   ```env
   DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```

### 7. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Start server
```bash
python manage.py runserver
```

### 9. Open browser
```
http://127.0.0.1:8000/
```

---

## ⚡ Smart Input: Full Job Description OR Target Role
ResumeIQ accepts both:
1. **Full Job Descriptions:** Pasted multi-paragraph job postings with explicit requirements.
2. **Target Role Names:** Short job titles like *"Senior Full Stack Engineer"*, *"AI Developer"*, or *"Data Analyst"*. The engine intelligently infers standard industry-required skills, preferred tools, and typical experience so the candidate is accurately scored against the role.

---

## 🛡️ No Groq key? Still works!
The app features resilient multi-layer fallbacks:
- **Groq Outage / No Key:** Automated rule-based skill extraction (`skill_extractor.py`) using a 300+ technical skill catalog and regex pattern matching.
- **Semantic Matching:** TF-IDF character n-gram cosine similarity and SequenceMatcher string distance.

---

## 📊 ATS Score Formula
```
ATS Score = Keyword Match           x 0.35 (35%)
          + RAG Semantic Similarity x 0.35 (35%)
          + Experience Alignment    x 0.15 (15%)
          + Resume Quality Audit    x 0.15 (15%)
```

---

## 🔌 API Example (curl)
```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -F "resume_text=Python developer with 3 years Django, React, PostgreSQL..." \
  -F "job_description=Full Stack Engineer"
```

---

## 📁 Project Structure
```
ai_resume_analyzer/
├── config/                    # Django settings, urls, wsgi
├── resume_analyzer/
│   ├── services/
│   │   ├── llm_service.py         # Groq API client + JSON parser + role inference
│   │   ├── pdf_extractor.py       # PyPDF2 text extraction layer
│   │   ├── rag_skill_matcher.py   # Vector cosine similarity + skill variant decomposition
│   │   ├── scoring_engine.py      # 4-factor hybrid ATS scoring engine
│   │   ├── skill_extractor.py     # Rule-based fallback extractor (300+ skills catalog)
│   │   └── career_ai_engine.py    # Career intelligence, gaps, and roadmap generator
│   ├── tests/
│   │   └── test_rag_skill_matcher.py # Unit test suite
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── templates/                 # Modern HTML templates
├── docs/                      # Comprehensive engineering specifications
├── .env.example
├── requirements.txt
└── manage.py
```

---

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| **Backend** | Django 4.2 LTS, Django REST Framework |
| **AI / LLM** | Groq API (Llama 3.3 70B, Qwen 3.6 27B) |
| **Vector & RAG** | SentenceTransformers (`all-MiniLM-L6-v2`), scikit-learn TF-IDF |
| **PDF Parsing** | PyPDF2 (binary stream text extractor) |
| **Database** | PostgreSQL (Supabase / Production) / SQLite (Local) |
| **Frontend** | Django Templates, Vanilla JS (ES6+), Modern Responsive CSS |

