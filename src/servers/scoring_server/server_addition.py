import duckdb


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
