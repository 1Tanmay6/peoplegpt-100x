import json
import duckdb
from .ats_scoring import ATSScorer, JobRequirements
from .smart_scoring import process_candidate


async def l1_score_resumes(db_path: str, scorer: ATSScorer, threshold: float = 40.0):

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

    job_req_dict = {
        'required_skills': job_requirements.required_skills,
        'preferred_skills': job_requirements.preferred_skills,
        'min_experience_years': job_requirements.min_experience_years,
        'required_education': job_requirements.required_education,
        'industry_keywords': job_requirements.industry_keywords,
        'job_title_keywords': job_requirements.job_title_keywords,
        'extra_information': job_requirements.extra_information,
        'location_preference': job_requirements.location_preference
    }

    for candidate_resume in resumes:
        resume_id = candidate_resume[0]
        name = candidate_resume[1]

        # Get detailed evaluation
        evaluation = await process_candidate(candidate_resume, job_requirements=job_req_dict)

        # Extract scores from the new structure
        scores = evaluation.get('scores', {})
        final_score = scores.get('final_score', 0)
        is_adequate = scores.get('is_adequate', False)
        recommended_level = scores.get('recommended_level', 'entry')

        # Get component breakdowns
        breakdowns = scores.get('breakdowns', {})

        # Store the score in the database
        conn.execute("""
            UPDATE resumes
            SET smart_score = ?, smart_passed = ?
            WHERE id = ?
        """, [final_score, is_adequate, resume_id])

        # Display detailed results
        print(f"\nEvaluating {name} (ID: {resume_id}):")
        print("-" * 50)
        print(f"Final Score: {final_score:.1f}")
        print(f"Level: {recommended_level}")
        print(f"Pass Status: {'PASS' if is_adequate else 'FAIL'}")
        print("\nComponent Scores:")
        for component, details in breakdowns.items():
            print(
                f"• {component.replace('_', ' ').title()}: {details.get('score', 0):.1f}")
        print("-" * 50)


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

if __name__ == "__main__":
    import asyncio
    example_job_requirements = JobRequirements(
        required_skills=['Python', 'Machine Learning',
                         'SQL', 'Statistics', 'Data Analysis'],
        preferred_skills=['TensorFlow',
                          'Deep Learning', 'AWS', 'Docker', 'MLOps'],
        min_experience_years=0,
        required_education='Bachleor Degree',
        industry_keywords=['Python', "Data Science", "Data Driven"],
        job_title_keywords=['data scientist',
                            'machine learning', 'analyst', 'AI engineer'],
        extra_information=[]
    )
    db_path = '/home/tanmaypatil/Documents/100x/db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb'
    asyncio.run(score(db_path, example_job_requirements))
