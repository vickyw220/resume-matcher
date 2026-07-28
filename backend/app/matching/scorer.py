import json
import re
import os

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

def generate_suggestions(missing_skills: set, jd_text: str) -> list:
    suggestions = []
    for skill in sorted(missing_skills):
        mentions = count_mentions(skill, jd_text)
        if mentions > 1:
            suggestions.append(
                f"Consider adding '{skill.title()}' — it's mentioned {mentions} times in the job description but not found in your resume."
            )
        else:
            suggestions.append(
                f"Consider adding '{skill.title()}' — it's mentioned in the job description but not found in your resume."
            )
    return suggestions

def score_match(resume_text: str, jd_text: str) -> dict:
    skills_db = load_skills_db()
    jd_skills = extract_skills(jd_text, skills_db)
    resume_skills = extract_skills(resume_text, skills_db)

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills

    match_score = round(len(matched) / len(jd_skills), 2) if jd_skills else 0.0
    suggestions = generate_suggestions(missing, jd_text)

    return {
        "match_score": match_score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "suggestions": suggestions,
    }