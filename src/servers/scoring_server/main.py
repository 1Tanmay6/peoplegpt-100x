import json
import duckdb
from .ats_scoring import ATSScorer, JobRequirements
from .smart_scoring import process_candidate


async def l1_score_resumes(db_path: str, scorer: ATSScorer, threshold: float = 55.0):

    conn = duckdb.connect(db_path)

    resumes = conn.execute(
        "SELECT id, raw FROM resumes;").fetchall()

    for resume_id, resume_text in resumes:
        ats_score = scorer.calculate_overall_score(json.loads(resume_text))
        ats_passed = ats_score['overall_score'] >= threshold

        conn.execute("""
            UPDATE resumes
            SET ats_score = ?, ats_passed = ?
            WHERE id = ?
        """, [ats_score['overall_score'], ats_passed, resume_id])

        print(
            f"Updated resume ID {resume_id}: Score={ats_score}, Passed={ats_passed}")


async def l2_score_resumes(db_path: str, job_requirements: JobRequirements):
    conn = duckdb.connect(db_path)

    resumes = conn.execute(
        "SELECT id, name, email, phone, job_id, raw FROM resumes;").fetchall()

    for candidate_resume in resumes:
        resume_id = candidate_resume[0]
        result = await process_candidate(candidate_resume)
        conn.execute("""
            UPDATE resumes
            SET smart_score = ?, smart_passed = ?
            WHERE id = ?
        """, [result['final_score'], result['is_adequate'], resume_id])


async def score(db_path: str, job_requirements: JobRequirements):
    conn = duckdb.connect(db_path)

    for column, dtype in [("ats_score", "DOUBLE"), ("ats_passed", "BOOLEAN"), ("smart_score", "DOUBLE"), ("smart_passed", "BOOLEAN")]:
        try:
            conn.execute(
                f"ALTER TABLE resumes ADD COLUMN {column} {dtype};")
        except duckdb.CatalogException:
            pass

    await l1_score_resumes(
        db_path, scorer=ATSScorer(job_requirements))

    await l2_score_resumes(
        db_path=db_path, job_requirements=job_requirements
    )


# '/home/tanmaypatil/Documents/100x/db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb'
