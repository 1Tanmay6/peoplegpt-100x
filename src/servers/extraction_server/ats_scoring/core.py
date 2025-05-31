import json
import duckdb
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any


def load_all_resumes_from_duckdb(duckdb_path: str, table_name: str = "resumes") -> List[Dict[str, Any]]:
    """
    Connects to the given DuckDB file (or in-memory if duckdb_path=":memory:")
    and selects all JSON blobs from the specified table. It returns a list of
    Python dicts (parsed JSON).
    """
    # Connect to DuckDB (if duckdb_path=":memory:", it’s an in‐memory database)
    con = duckdb.connect(database=duckdb_path, read_only=False)

    # Fetch all rows from the resumes table; assume column "data" holds a JSON string
    query = f"SELECT raw FROM {table_name};"
    # returns a pandas DataFrame with one column "data"
    df = con.execute(query).fetchdf()

    resumes: List[Dict[str, Any]] = []
    for idx, row in df.iterrows():
        json_str = row["raw"]
        try:
            resume_dict = json.loads(json_str)
        except Exception as e:
            # In case some JSON is invalid, skip or handle as needed
            print(f"Warning: couldn't parse JSON for row {idx}: {e}")
            continue
        resumes.append(resume_dict)

    con.close()
    return resumes


def extract_resume_text(resume: Dict[str, Any]) -> str:
    """
    Given a parsed resume dictionary, extract and concatenate:
      - headline/title
      - profile summary
      - all skill strings
      - (optionally) past job titles/sections, etc.
    Adjust this to match your actual JSON structure.
    """
    pieces: List[str] = []

    # 1) Headline / Title (if exists)
    headline = resume.get("personal_information", {}).get("headline", "")
    if headline:
        pieces.append(str(headline).strip())

    # 2) Profile summary
    summary = resume.get("summary", {}).get("profile", "")
    if summary:
        pieces.append(str(summary).strip())

    # 3) Skills (flatten the "skill_values" array)
    skill_lines = resume.get("skill", {}).get("skill_values", [])
    for skill_line in skill_lines:
        # Each skill_line might be like "Languages: Python, SQL"
        # We just append the entire string (or split on ":" if you want sub‐keywords)
        pieces.append(str(skill_line).strip())

    # 4) (Optional) Past job titles or experience descriptions (if you have them)
    #    e.g., if resume has an array "work_experience":[{"title":..., "description":...}, ...]
    work_history = resume.get("work_experience", [])
    if isinstance(work_history, list):
        for job in work_history:
            title = job.get("job_title", "")
            desc = job.get("description", "")
            if title:
                pieces.append(str(title).strip())
            if desc:
                pieces.append(str(desc).strip())

    # 5) (Optional) Education or Projects, etc.
    #    Add more sections if your JSON contains them, following the same pattern.

    # Finally concatenate everything into one big text blob:
    text_blob = " ".join([p.lower() for p in pieces if p])
    return text_blob


def compute_experience_score(candidate_years: float, required_years: float) -> float:
    """
    Simple rule: 
      - If candidate_years >= required_years: score = 1.0
      - If candidate_years is slightly less (say within 1 year): score = 0.7
      - Otherwise: score = 0.3
    You can tweak thresholds as needed.
    """
    if candidate_years is None:
        return 0.0  # no info => worst case
    try:
        cand = float(candidate_years)
        req = float(required_years)
    except:
        return 0.0

    if cand >= req:
        return 1.0
    elif (req - cand) <= 1.0:
        return 0.7
    else:
        return 0.3


def compute_title_match_score(resume_headline: str, job_title: str) -> float:
    """
    If the resume’s headline (or current title) contains any of the “keywords”
    from the job title (e.g. ‘data scientist’, ‘ml engineer’), give a boost.
      - Exact match or partial word match -> 1.0
      - Otherwise -> 0.5
    """
    if not resume_headline:
        return 0.0
    r = resume_headline.lower()
    jt = job_title.lower()
    # Split job_title into words/phrases
    keywords = [kw.strip() for kw in jt.split() if len(kw) > 2]
    for kw in keywords:
        if kw in r:
            return 1.0
    return 0.5


def compute_skill_overlap_score(candidate_skills: List[str], job_skills: List[str]) -> float:
    """
    Straightforward measure: fraction of job_skills that appear in candidate_skills.
    Then clamp between 0.0 and 1.0.
    E.g. if job requires ["python", "pytorch", "aws"] and candidate has ["python","sql","docker"]:
      overlap = 1/3 = 0.333 -> return that value.
    If job_skills is empty, just return 0.0.
    """
    if not job_skills:
        return 0.0
    cand_set = set([s.lower() for s in candidate_skills if s])
    job_set = set([s.lower() for s in job_skills if s])
    if len(job_set) == 0:
        return 0.0
    intersection = cand_set.intersection(job_set)
    return len(intersection) / len(job_set)


def rank_resumes(
    job_description: Dict[str, Any],
    resumes: List[Dict[str, Any]],
    tfidf_stopwords: str = "english",
    weights: Dict[str, float] = None
) -> pd.DataFrame:
    """
    Given a single job_description (a dict) and a list of resumes (each a dict),
    compute a final score per resume by combining:
      1) TF-IDF cosine similarity between job_text and each resume_text
      2) Title‐match rule
      3) Experience rule
      4) Skill overlap rule

    weights: a dict that specifies how to weigh each sub‐score. For example:
      {
        "tfidf": 0.4,
        "title": 0.2,
        "experience": 0.2,
        "skill_overlap": 0.2
      }
    If weights is None, we default to equal-ish weights.
    """
    if weights is None:
        weights = {
            "tfidf": 0.35,
            "title": 0.25,
            "experience": 0.15,
            "skill_overlap": 0.25,
        }

    # 1) Build the “job_text_blob” from job_description fields
    job_title = job_description.get("title", "")
    job_summary = job_description.get("description", "")
    job_skills_list = []
    # If job_description["skills"] is a comma‐separated string, split it:
    raw_skills = job_description.get("skills", "")
    if isinstance(raw_skills, str):
        # Example: "Python, PyTorch, HuggingFace"
        job_skills_list = [s.strip().lower()
                           for s in raw_skills.split(",") if s.strip()]
    elif isinstance(raw_skills, list):
        job_skills_list = [s.strip().lower()
                           for s in raw_skills if isinstance(s, str)]
    else:
        job_skills_list = []

    # Concatenate:
    job_text_blob = " ".join(
        [job_title, job_summary, " ".join(job_skills_list)]).lower()

    # 2) For each resume, extract a text blob and also gather structured fields
    resume_texts: List[str] = []
    # will hold headline, experience_years, skill_list
    resume_structured: List[Dict[str, Any]] = []
    for resume in resumes:
        # a) Text for TF-IDF:
        txt = extract_resume_text(resume)
        resume_texts.append(txt)

        # b) Structured fields:
        headline = resume.get("personal_information", {}).get("headline", "")

        exp_years = resume.get("experience_years", None)
        # If your JSON instead has nested years per job, you might sum them manually;
        # here we assume a flat number field.

        # Build a flat list of individual skill keywords:
        skill_lines = resume.get("skill", {}).get("skill_values", [])
        flat_skill_list: List[str] = []
        for line in skill_lines:
            # e.g. "Languages: Python, SQL" -> ["python","sql"]
            if ":" in line:
                parts = line.split(":", 1)
                subs = [s.strip().lower()
                        for s in parts[1].split(",") if s.strip()]
                flat_skill_list.extend(subs)
            else:
                flat_skill_list.append(line.strip().lower())

        resume_structured.append({
            "headline": str(headline),
            "exp_years": exp_years,
            "skill_list": flat_skill_list
        })

    # 3) Compute TF-IDF similarity between job_text_blob and each resume_text
    vectorizer = TfidfVectorizer(stop_words=tfidf_stopwords)
    # first element is job, then resumes
    corpus = [job_text_blob] + resume_texts
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # cosine similarity of job (row 0) against each resume (rows 1..N)
    cosine_similarities = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # 4) For each resume, compute the sub-scores (title, experience, skill overlap)
    scores: List[Dict[str, Any]] = []
    req_exp = job_description.get("experience_required", 0)
    for idx, resume in enumerate(resumes):
        # TF-IDF score:
        tfidf_score = float(cosine_similarities[idx])

        # Title match score:
        title_score = compute_title_match_score(
            resume_structured[idx]["headline"], job_title
        )

        # Experience score:
        exp_score = compute_experience_score(
            resume_structured[idx]["exp_years"], req_exp
        )

        # Skill overlap score:
        skill_score = compute_skill_overlap_score(
            resume_structured[idx]["skill_list"], job_skills_list
        )

        # Combine according to weights
        final_score = (
            weights["tfidf"] * tfidf_score
            + weights["title"] * title_score
            + weights["experience"] * exp_score
            + weights["skill_overlap"] * skill_score
        )

        # Truncate or round fields as desired
        scores.append({
            "resume_index": idx,
            "candidate_name": resume.get("personal_information", {}).get("name", "Unknown"),
            "headline": resume_structured[idx]["headline"],
            "experience_years": resume_structured[idx]["exp_years"],
            "skill_overlap_frac": round(skill_score, 4),
            "tfidf_score": round(tfidf_score, 4),
            "title_score": round(title_score, 4),
            "experience_score": round(exp_score, 4),
            "final_score": round(final_score, 4),
        })

    # 5) Create DataFrame, sort by final_score descending
    df = pd.DataFrame(scores)
    df_sorted = df.sort_values(
        by="final_score", ascending=False).reset_index(drop=True)
    return df_sorted


# =========================
# Example usage of the above functions:
# =========================
if __name__ == "__main__":
    # 1) Define your DuckDB path (or ":memory:" if you want an in‐memory DB).
    duckdb_path = "/home/user/my_candidates.duckdb"  # adjust as needed

    # 2) Load all resumes from DuckDB:
    all_resumes = load_all_resumes_from_duckdb(
        duckdb_path, table_name="resumes")

    # 3) Define a single job description you want to match against:
    job_desc = {
        "title": "Data Scientist – NLP and Deep Learning",
        "description": (
            "We are looking for a data scientist with strong NLP experience, "
            "familiarity with Transformers, PyTorch, and deploying models on AWS. "
            "You will work on large text‐corpus modeling and productionizing pipelines."
        ),
        "skills": "Python, PyTorch, HuggingFace, AWS, NLP, Transformers",
        "experience_required": 2.0  # in years
    }

    # 4) Define custom weights if you want (optional). Otherwise None.
    custom_weights = {
        "tfidf": 0.4,
        "title": 0.2,
        "experience": 0.2,
        "skill_overlap": 0.2
    }

    # 5) Rank all resumes:
    ranked_resumes_df = rank_resumes(
        job_desc, all_resumes, weights=custom_weights)

    # 6) Show top 10 matches:
    print(ranked_resumes_df.head(10))

    # 7) Optionally: save to CSV
    # ranked_resumes_df.to_csv("ranked_resumes_for_job_XYZ.csv", index=False)
