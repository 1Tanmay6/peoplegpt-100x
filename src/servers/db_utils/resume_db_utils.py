import json
import uuid
import duckdb
import asyncio
from pathlib import Path
from typing import List, Optional


class ResumeDBManager:
    """
    Encapsulates all DuckDB operations:
      • connecting/closing
      • creating tables
      • inserting one resume row
      • identifying duplicates.
    """

    def __init__(self, db_path: str):
        self.con = duckdb.connect(database=db_path)
        self._ensure_main_table()
        self.con.execute("DROP TABLE IF EXISTS duplicate_resumes;")

    def _ensure_main_table(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id       TEXT PRIMARY KEY,
                name     TEXT,
                email    TEXT,
                phone    TEXT,
                job_id   TEXT,
                raw      JSON,
                file_path TEXT
            );
        """)

    def insert_resume_row(
        self,
        resume_id: str,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        job_id: str,
        raw_json_str: str,
        file_path: str
    ):
        self.con.execute(
            """
            INSERT INTO resumes (id, name, email, phone, job_id, raw, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [resume_id, name, email, phone, job_id, raw_json_str, file_path]
        )

    def identify_and_store_duplicates(self) -> int:
        """
        Identifies duplicates by (name, email) and moves all but one into `duplicate_resumes`,
        with a foreign key reference to the original resume's ID.
        Returns the number of rows moved.
        """
        self.con.execute("DROP TABLE IF EXISTS duplicate_resumes;")

        self.con.execute("""
            CREATE TABLE duplicate_resumes AS
            WITH grouped AS (
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    job_id,
                    raw,
                    ROW_NUMBER() OVER (
                        PARTITION BY name, email
                        ORDER BY id
                    ) AS row_num,
                    FIRST_VALUE(id) OVER (
                        PARTITION BY name, email
                        ORDER BY id
                    ) AS original_id
                FROM resumes
                WHERE name IS NOT NULL AND email IS NOT NULL
            )
            SELECT 
                id,
                name,
                email,
                phone,
                job_id,
                raw,
                original_id AS duplicate_of_id
            FROM grouped
            WHERE row_num > 1;
        """)

        self.con.execute("""
            DELETE FROM resumes
            WHERE id IN (SELECT id FROM duplicate_resumes);
        """)

        dup_count = self.con.execute(
            "SELECT COUNT(*) FROM duplicate_resumes;").fetchone()[0]
        return dup_count

    def close(self):
        self.con.close()


async def parse_and_insert_file(
    file_path: str,
    job_id: str,
    db_manager: ResumeDBManager,
    parser: any,
    db_lock: asyncio.Lock
):
    try:
        parsed_dict = await parser.parse(file_path)
    except Exception as e:
        print(f"[!] Failed to parse '{file_path}': {e}")
        return

    name = (parsed_dict.get("personal_information").get("first_name", "").strip() + " " +
            parsed_dict.get("personal_information").get("last_name", "").strip()) or None
    email = parsed_dict.get("personal_information").get(
        "email_address", "").strip() or None
    phone = parsed_dict.get("personal_information").get(
        "phone_number", "").strip() or None

    resume_id = str(uuid.uuid4())
    raw_json_str = json.dumps(parsed_dict)

    async with db_lock:
        try:
            db_manager.insert_resume_row(
                resume_id=resume_id,
                name=name,
                email=email,
                phone=phone,
                job_id=job_id,
                raw_json_str=raw_json_str,
                file_path=file_path
            )
            print(f"[+] Inserted '{file_path}' (resume_id={resume_id})")
        except Exception as e:
            print(f"[!] DB insert error for '{file_path}': {e}")


def collect_resume_paths(folder_path: str, extensions: List[str] = None) -> List[str]:
    if extensions is None:
        extensions = [".pdf", ".docx", ".doc"]

    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Folder not found or not a directory: {folder_path}")

    all_paths = []
    for ext in extensions:
        all_paths.extend([str(p) for p in folder.rglob(f"*{ext}")])

    return all_paths


async def process_folder_concurrently(
    folder_path: str,
    job_id: str,
    db_path: str,
    parser: any,
):
    db_manager = ResumeDBManager(db_path=db_path)
    db_lock = asyncio.Lock()

    try:
        resume_paths = collect_resume_paths(folder_path)
    except ValueError as ve:
        print(f"[!] {ve}")
        db_manager.close()
        return

    if not resume_paths:
        print(f"[!] No resume files found under '{folder_path}'")
        db_manager.close()
        return

    tasks = [
        parse_and_insert_file(
            file_path=path,
            job_id=job_id,
            db_manager=db_manager,
            parser=parser,
            db_lock=db_lock
        ) for path in resume_paths
    ]

    await asyncio.gather(*tasks)

    dup_count = db_manager.identify_and_store_duplicates()
    print(
        f"[!] Found {dup_count} duplicate resume row(s) → stored in 'duplicate_resumes'.")

    db_manager.close()
