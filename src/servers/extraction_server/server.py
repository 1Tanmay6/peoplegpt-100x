import os
import asyncio
from ..db_utils import process_folder_concurrently
from .resume_parser import ResumeParser
from ..connectors import OllamaConnector


def main(
    connector,
    folder_path: str,
    job_id: str
):
    db_filename = f"db/resumes_{job_id}.duckdb"
    db_path = os.path.abspath(db_filename)

    parser = ResumeParser(connector=connector)

    print(f"→ Using DuckDB file: {db_path}")
    print(f"→ Scanning folder   : {folder_path}")
    print(f"→ Tagging job_id    : {job_id}\n")

    asyncio.run(process_folder_concurrently(
        folder_path=folder_path,
        job_id=job_id,
        db_path=db_path,
        parser=parser
    ))

    print("\n All done.")
    print(f"  • All resumes →   Table `resumes` in {db_path}")
    print(f"  • Duplicates →    Table `duplicate_resumes` in {db_path}")


if __name__ == "__main__":
    import uuid
    connector = OllamaConnector(
        thinking='non-thinking', model=os.getenv('ollama_model_name_non_thinking'))
    DEFAULT_FOLDER_PATH = "/home/tanmaypatil/Downloads/Documents"
    DEFAULT_JOB_ID = uuid.uuid1()

    main(connector=connector, folder_path=DEFAULT_FOLDER_PATH, job_id=DEFAULT_JOB_ID)
