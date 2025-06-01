import os
from pathlib import Path
from ..db_utils import process_folder_concurrently
from .resume_parser import ResumeParser


def get_db_path(job_id: str) -> str:
    project_root = Path(__file__).resolve().parent
    db_dir = project_root / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / f"resumes_{job_id}.duckdb")


async def parse(
    connector,
    folder_path: str,
    job_id: str
):
    db_filename = f"db/{job_id}"
    os.makedirs(db_filename, exist_ok=True)
    db_filename += f"/resumes_{job_id}.duckdb"
    db_path = os.path.abspath(db_filename)

    parser = ResumeParser(connector=connector)

    print(f"→ Using DuckDB file: {db_path}")
    print(f"→ Scanning folder   : {folder_path}")
    print(f"→ Tagging job_id    : {job_id}\n")

    await process_folder_concurrently(
        folder_path=folder_path,
        job_id=job_id,
        db_path=db_path,
        parser=parser
    )

    print("\n All done.")
    print(f"  • All resumes →   Table `resumes` in {db_path}")
    print(f"  • Duplicates →    Table `duplicate_resumes` in {db_path}")

    return db_path
