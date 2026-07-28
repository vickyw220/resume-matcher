# Resume Matcher

🔗 **Live demo:** [resume-matcher-five-mauve.vercel.app](https://resume-matcher-five-mauve.vercel.app)

A tool that compares your resume against a job description and tells you how well you match — including which skills you already have and which ones you're missing.

I built this to solve my own problem: applying to entry-level software jobs and not knowing why I wasn't getting responses. This tells you exactly what a job posting is looking for that your resume doesn't currently show.

## What it does

1. Upload your resume as a PDF
2. Paste in a job description
3. Get back:
   - A match score (0–1)
   - The skills from the job description that your resume already covers
   - The skills the job description mentions that your resume is missing

## How it works

- Extracts text from your uploaded PDF resume
- Scans both the resume and job description against a reference list of common tech skills, tools, and soft skills
- Compares the two sets and calculates a match score based on overlap
- For any skill flagged as missing, runs a second pass using sentence embeddings to check whether a semantically similar phrase already exists in the resume (catching things like "teamwork" matching "collaborated on a cross-functional team," which exact keyword matching would miss)
- Generates specific, actionable suggestions for genuinely missing skills — not just naming the gap, but how to realistically gain exposure to it and an example of how to phrase it on a resume

The keyword layer is intentionally simple and transparent — every match or miss can be explained by a plain lookup, no black box. The semantic layer's similarity threshold wasn't picked arbitrarily either: it was tuned by running real skills against real resume text and inspecting the actual similarity scores. That process caught a real bug — short fragments like section headers ("PROJECTS") were scoring anomalously high against short skill names, producing false matches — which was fixed by filtering resume text into meaningful, multi-word phrases before comparing.

## Quick PSA

The match score is a practice signal to help you tailor your resume's wording — it is not a reflection of any real company's actual ATS scoring system (those are proprietary and vary by employer). A high score doesn't guarantee an interview, and a lower score doesn't mean you shouldn't apply — human reviewers weigh things this tool can't see, like portfolio quality, referrals, and interview performance. Use it to catch wording gaps, not as a pass/fail gate on whether to apply.

## Tech stack

- **Backend:** Python, FastAPI
- **PDF parsing:** pdfplumber
- **Semantic matching:** sentence-transformers (all-MiniLM-L6-v2)
- **Frontend:** React (Vite)
- **Server:** Uvicorn
- **Deployment:** Railway (backend), Vercel (frontend)

## Running it locally

You'll need two terminal windows open at the same time — one for the backend, one for the frontend.

### Backend

```bash
git clone https://github.com/vickyw220/resume-matcher.git
cd resume-matcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`. You can also test it directly at `http://127.0.0.1:8000/docs` without the frontend.

### Frontend

In a separate terminal:

```bash
cd resume-matcher/frontend
npm install
npm run dev
```

This will print a local URL (usually `http://localhost:5173` or `5174`) — open that in your browser to use the app.

## Project structure

```
resume-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py              # API routes + CORS config
│   │   ├── parsing/
│   │   │   └── resume_parser.py # PDF text extraction
│   │   ├── matching/
│   │   │   └── scorer.py        # Skill matching, semantic matching, and suggestion logic
│   │   ├── skills_db.json       # Reference list of skills to match against
│   │   └── skill_tips.json      # Actionable guidance per skill (how to gain it + example bullet)
│   └── tests/
├── frontend/
│   └── src/
│       ├── App.jsx              # Upload form + results display
│       └── App.css
├── requirements.txt
└── README.md
```

## Roadmap

- [x] Actionable suggestions (e.g. "Consider adding 'AWS' — it's mentioned in the job description but not found in your resume")
- [x] Larger, more complete skills reference list
- [x] Simple frontend so it's usable without the API docs page
- [x] Semantic matching using sentence embeddings (catch synonyms and rephrasing, not just exact keyword matches)
- [x] Rich, actionable suggestions with specific guidance on how to gain each missing skill and an example resume bullet
- [ ] Save scan history so users can track improvement over time

## Why I built this this way

Started with a simple, explainable keyword-matching approach rather than jumping straight to a more complex NLP model — this let me ship something working quickly, and it gives a clear baseline to compare a more advanced version against later.