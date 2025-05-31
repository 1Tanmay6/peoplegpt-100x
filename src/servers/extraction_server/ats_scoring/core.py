# Job Matching and Ranking System

import json
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

# Load Tanmay's Profile (Insert actual profile JSON or load from file)
with open("/home/tanmaypatil/Documents/100x/docs/resume.json") as f:
    profile = json.load(f)

# Extract keywords from profile
profile_keywords = []
for skill_line in profile["skill"]["skill_values"]:
    parts = skill_line.split(":")
    if len(parts) > 1:
        profile_keywords.extend([s.strip() for s in parts[1].split(",")])

profile_keywords = list(set([kw.lower() for kw in profile_keywords]))
profile_text_blob = " ".join(profile_keywords)

# Profile Title & Summary
profile_title = profile["personal_information"]["headline"]
profile_summary = profile["summary"]["profile"]

profile_text = f"{profile_title} {profile_summary} {profile_text_blob}"

# === Function to Rank Job Descriptions === #


def rank_jobs(job_descriptions: List[Dict], profile_text: str) -> pd.DataFrame:
    # Vectorize the profile and job descriptions using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    job_texts = [
        f"{job['title']} {job.get('description', '')} {job.get('skills', '')}" for job in job_descriptions]
    corpus = [profile_text] + job_texts
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity between profile and each job
    similarities = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Score each job
    scores = []
    for idx, job in enumerate(job_descriptions):
        job_score = similarities[idx]

        # Check if title contains data scientist related role
        title_score = 1.0 if any(t in job['title'].lower() for t in [
                                 "data scientist", "ml engineer", "machine learning"]) else 0.5

        # Check if experience required is suitable
        exp_required = job.get("experience_required", 0)
        exp_score = 1.0 if exp_required <= 1 else 0.3

        final_score = 0.35 * job_score + 0.25 * title_score + 0.15 * exp_score
        scores.append({
            "title": job['title'],
            "company": job.get('company', 'N/A'),
            "location": job.get('location', 'N/A'),
            "score": round(final_score, 4),
            "description": job.get('description', '')[:200] + '...'
        })

    df = pd.DataFrame(scores).sort_values(
        by="score", ascending=False).reset_index(drop=True)
    return df

# === Example Usage === #


# Replace with real job descriptions loaded from a JSON or API
example_jobs = [
    {
        "title": "Data Scientist - NLP",
        "company": "TechAI Solutions",
        "location": "Bangalore, India",
        "description": "Looking for a data scientist with experience in NLP, Transformers, and Deep Learning.",
        "skills": "Python, PyTorch, HuggingFace, LLMs, Transformers",
        "experience_required": 0
    },
    {
        "title": "Junior Machine Learning Engineer",
        "company": "InnovateML",
        "location": "Remote",
        "description": "Entry-level role focusing on predictive modeling and model deployment.",
        "skills": "Python, Scikit-learn, Docker, AWS",
        "experience_required": 1
    },
    {
        "title": "Senior Data Analyst",
        "company": "DataCorp",
        "location": "Mumbai",
        "description": "Requires 3+ years of experience in data analytics and business intelligence.",
        "skills": "SQL, Power BI, Excel",
        "experience_required": 3
    }
]

ranked_df = rank_jobs(example_jobs, profile_text)
print(ranked_df)

# Optionally save to CSV
# ranked_df.to_csv("ranked_jobs.csv", index=False)
