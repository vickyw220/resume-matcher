import json
import re
import os
from sentence_transformers import SentenceTransformer, util

# Load the embedding model once when the server starts (not on every request —
# loading it fresh each time would be slow and wasteful)
_model = SentenceTransformer("all-MiniLM-L6-v2")

# How similar two phrases need to be (0-1 scale) to count as a semantic match.
# Tuned using real test data: genuine paraphrase matches (e.g. "teamwork" ~
# "team collaboration sessions") scored ~0.50, while unrelated skills scored
# ~0.28 or lower. 0.45 sits comfortably between those two clusters.
SEMANTIC_THRESHOLD = 0.45


def load_skills_db():
    path = os.path.join(os.path.dirname(__file__), "..", "skills_db.json")
    with open(path, "r") as f:
        data = json.load(f)
    all_skills = []
    for category in data.values():
        all_skills.extend(category)
    return all_skills


def extract_skills(text: str, skills_db: list) -> set:
    text_lower = text.lower()
    found = set()
    for skill in skills_db:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def count_mentions(skill: str, text: str) -> int:
    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
    return len(re.findall(pattern, text.lower()))


def split_into_phrases(text: str) -> list:
    """Break resume text into bullet-sized chunks so we can compare each one
    against a missing skill, rather than comparing against the whole resume
    as one giant blob (which would dilute the meaning).

    Only splits on newlines/bullets (not periods) since PDF line-wrapping
    means periods show up mid-sentence in unpredictable places. Also filters
    out short fragments (headers, single words) since these can score
    anomalously high against short skill queries and produce false matches."""
    lines = re.split(r'[\n\u2022•]', text)
    phrases = [line.strip() for line in lines if line.strip()]
    # Require at least 4 words so section headers and stray fragments
    # ("PROJECTS", "EXPERIENCE", "environments") don't get treated as
    # meaningful sentences
    return [p for p in phrases if len(p.split()) >= 4]


def find_semantic_matches(missing_skills: set, resume_text: str) -> dict:
    """For each skill the keyword pass flagged as missing, check whether a
    semantically similar phrase already exists somewhere in the resume.
    Returns a dict mapping skill -> best matching resume phrase (only for
    skills that clear the similarity threshold)."""
    if not missing_skills:
        return {}

    resume_phrases = split_into_phrases(resume_text)
    if not resume_phrases:
        return {}

    phrase_embeddings = _model.encode(resume_phrases, convert_to_tensor=True)
    skill_list = sorted(missing_skills)
    skill_embeddings = _model.encode(skill_list, convert_to_tensor=True)

    semantic_matches = {}
    for i, skill in enumerate(skill_list):
        similarities = util.cos_sim(skill_embeddings[i], phrase_embeddings)[0]
        best_idx = int(similarities.argmax())
        best_score = float(similarities[best_idx])
        if best_score >= SEMANTIC_THRESHOLD:
            semantic_matches[skill] = {
                "matched_phrase": resume_phrases[best_idx],
                "similarity": round(best_score, 2),
            }
    return semantic_matches


def load_skill_tips():
    path = os.path.join(os.path.dirname(__file__), "..", "skill_tips.json")
    with open(path, "r") as f:
        return json.load(f)


def generate_suggestions(missing_skills: set, jd_text: str) -> list:
    tips = load_skill_tips()
    suggestions = []

    for skill in sorted(missing_skills):
        mentions = count_mentions(skill, jd_text)
        frequency_note = (
            f"it's mentioned {mentions} times in the job description"
            if mentions > 1
            else "it's mentioned in the job description"
        )

        entry = tips.get(skill)

        if entry:
            suggestions.append({
                "skill": skill,
                "summary": f"'{skill.title()}' is missing from your resume — {frequency_note}.",
                "how_to_gain": entry["how_to_gain"],
                "example_bullet": entry["example_bullet"],
            })
        else:
            # Generic fallback for skills without a specific tip entry
            suggestions.append({
                "skill": skill,
                "summary": f"'{skill.title()}' is missing from your resume — {frequency_note}.",
                "how_to_gain": (
                    f"If you have any exposure to {skill} — through coursework, a project, or self-study — "
                    f"make sure it's explicitly named on your resume rather than implied. If you genuinely "
                    f"don't have experience with it yet, look for a small project or free tutorial that lets "
                    f"you use it hands-on before your next application, so you have something real to speak to."
                ),
                "example_bullet": (
                    f"Used {skill.title()} in [project/coursework name] to [what you built or accomplished]."
                ),
            })

    return suggestions


def score_match(resume_text: str, jd_text: str) -> dict:
    skills_db = load_skills_db()
    jd_skills = extract_skills(jd_text, skills_db)
    resume_skills = extract_skills(resume_text, skills_db)

    matched = jd_skills & resume_skills
    missing_after_keywords = jd_skills - resume_skills

    # Second pass: check if any "missing" skills are actually implied
    # elsewhere in the resume, just phrased differently
    semantic_matches = find_semantic_matches(missing_after_keywords, resume_text)

    truly_missing = missing_after_keywords - set(semantic_matches.keys())

    match_score = (
        round((len(matched) + len(semantic_matches)) / len(jd_skills), 2)
        if jd_skills else 0.0
    )

    suggestions = generate_suggestions(truly_missing, jd_text)

    return {
        "match_score": match_score,
        "matched_skills": sorted(matched),
        "semantically_matched_skills": [
            {
                "skill": skill,
                "found_as": info["matched_phrase"],
                "similarity": info["similarity"],
            }
            for skill, info in sorted(semantic_matches.items())
        ],
        "missing_skills": sorted(truly_missing),
        "suggestions": suggestions,
    }