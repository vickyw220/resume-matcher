"""
Quick debug script to see actual similarity scores between a skill
and resume phrases. Run this directly to tune SEMANTIC_THRESHOLD.

Usage: python debug_similarity.py
"""
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

resume_text = """
Collaborated with faculty and staff to support student success initiatives.
Collaborated within a team environment using Git version control.
Cross-Functional Collaboration, Leadership, Problem Solving, Communication, Mentoring.
Participated in Agile development processes, sprint planning, and team collaboration sessions.
"""

skills_to_test = ["teamwork", "stakeholder management", "kubernetes"]

phrases = [line.strip() for line in resume_text.split("\n") if len(line.strip()) > 5]
phrase_embeddings = model.encode(phrases, convert_to_tensor=True)

for skill in skills_to_test:
    skill_embedding = model.encode(skill, convert_to_tensor=True)
    similarities = util.cos_sim(skill_embedding, phrase_embeddings)[0]

    print(f"\n=== '{skill}' ===")
    # Show all phrases sorted by similarity, highest first
    scored = sorted(zip(phrases, similarities.tolist()), key=lambda x: -x[1])
    for phrase, score in scored:
        print(f"  {score:.3f}  {phrase}")