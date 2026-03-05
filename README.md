# AI Resume Analyzer & ATS-Based Job Matcher
### Django + Groq (Llama 3 - FREE) | Hybrid ATS Scoring Engine

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
venv\Scripts\activate           # Windows
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

### 6. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Start server
```bash
python manage.py runserver
```

### 8. Open browser
```
http://127.0.0.1:8000/
```

---

## No Groq key? Still works!
The app runs without any API key using built-in rule-based fallback.
Skill extraction uses regex. Scoring uses TF-IDF cosine similarity.

---

## ATS Score Formula
```
ATS Score = Keyword Match     x 0.40 (40%)
          + Semantic Similarity x 0.30 (30%)
          + Experience Match   x 0.20 (20%)
          + Resume Quality     x 0.10 (10%)
```

---

## API Example (curl)
```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -F "resume_text=Python developer with 3 years Django, React, PostgreSQL..." \
  -F "job_description=Looking for Django developer 2+ years experience..."
```

---

## Project Structure
```
ai_resume_analyzer/
├── config/                    # Django settings, urls, wsgi
├── resume_analyzer/
│   ├── services/
│   │   ├── llm_service.py     # Groq API + mock fallback
│   │   ├── pdf_extractor.py   # PDF text extraction
│   │   └── scoring_engine.py  # Hybrid ATS scoring engine
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── templates/                 # HTML templates
├── .env.example
├── requirements.txt
└── manage.py
```

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, DRF |
| AI/LLM | Groq API (Llama 3-8b) - FREE |
| Semantic Scoring | scikit-learn TF-IDF |
| PDF Parsing | PyPDF2 |
| Database | SQLite (dev) |
| Frontend | Django Templates + Vanilla JS |
