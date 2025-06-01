import duckdb
import json
from .outreach_generation import generate_failed_message, generate_passed_message
from .qa_generation import QAGenerator
from ..connectors import OllamaConnector, GroqConnector


async def update_passed_with_qa_and_message(con, generator: QAGenerator, job_requirements):

    # Fetch all passed resumes with their id and raw text
    passed = con.execute(
        "SELECT id, name, raw FROM passed_ranked_resumes").fetchall()

    for resume_id, name, raw_json in passed:
        # Generate Q&A as JSON string
        # should return list/dict
        qa_list = await generator.generate(resume_text=raw_json, job_descr=job_requirements)
        qa_json = json.dumps(qa_list)

        # Generate notification message string
        notif_msg = generate_passed_message(name)

        # Update the table
        con.execute("""
            UPDATE passed_ranked_resumes
            SET qa_generation = ?, notification_message = ?
            WHERE id = ?
        """, (qa_json, notif_msg, resume_id))


def update_failed_with_message(con):

    failed = con.execute("SELECT id, name FROM failed_resumes").fetchall()

    for resume_id, name in failed:
        notif_msg = generate_failed_message(name)
        con.execute("""
            UPDATE failed_resumes
            SET notification_message = ?
            WHERE id = ?
        """, (notif_msg, resume_id))


async def generate(db_path: str, job_requirements):
    con = duckdb.connect(db_path)
    connector = OllamaConnector(thinking='thinking')

    con.execute("""
    ALTER TABLE passed_ranked_resumes
    ADD COLUMN IF NOT EXISTS qa_generation VARCHAR;
    """)

    con.execute("""
        ALTER TABLE passed_ranked_resumes
        ADD COLUMN IF NOT EXISTS notification_message VARCHAR;
    """)

    con.execute("""
        ALTER TABLE failed_resumes
        ADD COLUMN IF NOT EXISTS notification_message VARCHAR;
    """)

    generator = QAGenerator(connector=connector)

    update_failed_with_message(con=con)

    await update_passed_with_qa_and_message(con=con, generator=generator, job_requirements=job_requirements)


def rerank_resumes(db_path: str):
    con = duckdb.connect(database=db_path)

    # Create passed_ranked_resumes table
    con.execute("""
        CREATE OR REPLACE TABLE passed_ranked_resumes AS
        SELECT 
            *, 
            (ats_score + smart_score) AS total_score
        FROM resumes
        WHERE ats_passed = TRUE AND smart_passed = TRUE
        ORDER BY total_score DESC;
    """)

    # Create failed_resumes table
    con.execute("""
        CREATE OR REPLACE TABLE failed_resumes AS
        SELECT *
        FROM resumes
        WHERE ats_passed = FALSE OR smart_passed = FALSE;
    """)

    con.close()
    print("Resumes processed successfully: 'passed_ranked_resumes' and 'failed_resumes' tables created.")


if __name__ == "__main__":
    from ..scoring_server.ats_scoring import JobRequirements
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

    rerank_resumes(
        db_path="/home/tanmaypatil/Documents/100x/db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb")
    import asyncio
    print(asyncio.run(generate(
        db_path="/home/tanmaypatil/Documents/100x/db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb",
        job_requirements=example_job_requirements
    )))
