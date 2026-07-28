# Resume Matcher

A tool that compares your resume against a job description and tells you how well you match — including which skills you already have and which ones you're missing.

I built this to solve my own problem: applying to entry-level software jobs and not knowing why I wasn't getting responses. This tells you exactly what a job posting is looking for that your resume doesn't currently show.

## What it does

1. Upload your resume as a PDF
2. Paste in a job description
3. Get back:
   - A match score (0–1)
   - The skills from the job description that your resume already covers
   - The skills the job description mentions that your resume is missing

## How it works (v1)

- Extracts text from your uploaded PDF resume
- Scans both the resume and job description against a reference list of common tech skills, tools, and soft skills
- Compares the two sets and calculates a match score based on overlap

This is intentionally simple and transparent right now — every match or miss can be explained by a plain keyword lookup, no black box. A planned v2 will add semantic matching (using sentence embeddings) so it can catch things like "team player" matching "teamwork," which simple keyword matching misses.

## Small PSA

The match score is a practice signal to help you tailor your resume's wording — it is not a reflection of any real company's actual ATS scoring system (those are proprietary and vary by employer). A high score doesn't guarantee an interview, and a lower score doesn't mean you shouldn't apply — human reviewers weigh things this tool can't see, like portfolio quality, referrals, and interview performance. Use it to catch wording gaps, not as a pass/fail gate on whether to apply.

## Tech stack

- **Backend:** Python, FastAPI
- **PDF parsing:** pdfplumber
- **Server:** Uvicorn

## Running it locally

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/vickyw220/resume-matcher.git
cd resume-matcher
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart pdfplumber
```

Start the server:

```bash
uvicorn backend.app.main:app --reload
```

Then open your browser to:

- `http://127.0.0.1:8000` — confirms the server is running
- `http://127.0.0.1:8000/docs` — interactive API docs where you can try it out directly (upload a PDF resume + paste a job description into the `/match-pdf` endpoint)

## Project structure

```
resume-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py              # API routes
│   │   ├── parsing/
│   │   │   └── resume_parser.py # PDF text extraction
│   │   ├── matching/
│   │   │   └── scorer.py        # Skill matching + scoring logic
│   │   └── skills_db.json       # Reference list of skills to match against
│   └── tests/
└── README.md
```

## Roadmap

- [ ] Semantic matching using sentence embeddings (catch synonyms and rephrasing, not just exact keyword matches)
- [ ] Actionable suggestions (e.g. "Consider adding 'AWS' — it appears 3 times in the job description")
- [ ] Simple frontend so it's usable without the API docs page
- [ ] Larger, more complete skills reference list
- [ ] Save scan history so users can track improvement over time

## Why I built this this way

Started with a simple, explainable keyword-matching approach rather than jumping straight to a more complex NLP model — this let me ship something working quickly, and it gives a clear baseline to compare a more advanced version against later.
