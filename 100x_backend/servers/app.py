# app.py

import posthog
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import TypedDict, List
import os
import asyncio
import time
import shutil
import uuid
import zipfile
import duckdb
from dotenv import load_dotenv
from pathlib import Path
from servers import GroqConnector, parse, score, JobRequirements, generate, rerank_resumes

load_dotenv()

# Initialize PostHog
# Replace with your PostHog API key
posthog.api_key = os.getenv("VITE_POSTHOG_API_KEY")
# Or your self-hosted PostHog instance URL
posthog.host = os.getenv("VITE_POSTHOG_HOST")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Or specify list like ["http://localhost:3000"]
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("groq_api_key")
model = os.getenv("groq_model_name")
# Initialize Ollama connector
conn = GroqConnector(api_key=api_key, model=model)

DEFAULT_FOLDER_PATH = "docs/uploads"
DB_DIR = "db"


# JobRequirements Pydantic wrapper
class JobRequirementsInput(TypedDict):
    """Job requirements for scoring"""
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: int
    required_education: str
    industry_keywords: List[str]
    job_title_keywords: List[str]
    extra_information: List[str]
    location_preference: str = ""


task_queue = asyncio.Queue()

# Background worker to process tasks sequentially


@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker())


async def worker():
    while True:
        task = await task_queue.get()
        try:
            await process_task(*task)
        except Exception as e:
            print(f"Task failed: {e}")
        finally:
            task_queue.task_done()


async def process_task(prompt, job_id, zip_file, result_future):
    start_time = time.monotonic()

    try:
        job_id = job_id or str(uuid.uuid1())

        # Track job start
        posthog.capture(
            'test-id',
            'backend_job_started',
            {
                'job_id': job_id,
                'filename': zip_file.filename,
                'prompt': prompt
            }
        )

        job_folder_path = os.path.join(DEFAULT_FOLDER_PATH, job_id)
        os.makedirs(job_folder_path, exist_ok=True)

        zip_path = os.path.join(job_folder_path, "resumes.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(zip_file.file, f)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(job_folder_path)

        llm_prompt = f"""
        Given a prompt from the user generate all the fields (make sure you use your knowledge but user's prompt is addressed at higher priority), convert the prompt into a useful and structured Job Requirements.

        Input:
        {prompt}
        """
        res = await conn.acall(conn.create_obj(structure=JobRequirementsInput), prompt=llm_prompt)

        job_requirements = JobRequirements(
            required_skills=res["required_skills"],
            preferred_skills=res["preferred_skills"],
            min_experience_years=res["min_experience_years"],
            required_education=res["required_education"],
            industry_keywords=res["industry_keywords"],
            job_title_keywords=res["job_title_keywords"],
            extra_information=res["extra_information"]
        )

        db_path = await parse(connector=conn, folder_path=job_folder_path, job_id=job_id)
        await score(db_path=db_path, job_requirements=job_requirements)
        rerank_resumes(db_path=db_path)
        await generate(db_path=db_path, job_requirements=job_requirements)

        con = duckdb.connect(db_path)
        res_all = con.execute("SELECT * FROM resumes;").fetch_df()
        res_all.to_excel(db_path.replace('.duckdb', '.xlsx'))
        res_pass = con.execute(
            "SELECT * FROM passed_ranked_resumes;").fetch_df()
        res_pass.to_excel(db_path.replace('.duckdb', '_pass.xlsx'))
        res_fail = con.execute("SELECT * FROM failed_resumes;").fetch_df()
        res_fail.to_excel(db_path.replace('.duckdb', '_fail.xlsx'))

        elapsed = time.monotonic() - start_time
        mins, secs = divmod(int(elapsed), 60)

        # Track successful job completion
        posthog.capture(
            'test-id',
            'backend_job_completed',
            {
                'job_id': job_id,
                'processing_time': f"{mins} min {secs} sec",
                'resumes_processed': len(res_all),
                'passed_resumes': len(res_pass),
                'failed_resumes': len(res_fail),
                'filename': zip_file.filename
            }
        )

        result_future.set_result({
            "message": "Upload and processing complete",
            "job_id": job_id,
            "prompt": prompt,
            "uploaded_zip_file": zip_file.filename,
            "db_path": db_path,
            "xlsx_path": db_path.replace('.duckdb', '.xlsx'),
            "pass_xlsx_path": db_path.replace('.duckdb', '_pass.xlsx'),
            "fail_xlsx_path": db_path.replace('.duckdb', '_fail.xlsx'),
            "processing_time": f"{mins} min {secs} sec"
        })

    except Exception as e:
        # Track job errors
        posthog.capture(
            'test-id',
            'backend_job_error',
            {
                'job_id': job_id,
                'error': str(e),
                'filename': zip_file.filename
            }
        )
        result_future.set_result(
            JSONResponse(status_code=500, content={"error": str(e)})
        )


@app.post("/upload_and_run")
async def upload_and_run(
    prompt: str = Form(...),
    job_id: str = Form(None),
    zip_file: UploadFile = File(...)
):
    # Track API request
    posthog.capture(
        'test-id',
        'upload_and_run_request',
        {
            'job_id': job_id or 'new',
            'filename': zip_file.filename
        }
    )
    result_future = asyncio.Future()
    await task_queue.put((prompt, job_id, zip_file, result_future))
    result = await result_future
    return result


@app.get("/get-history")
async def get_history():
    # Track history request
    posthog.capture('test-id', 'history_request', {})

    db_path = './db'

    res = {}
    abs_path = Path(db_path).resolve().absolute()
    for path, _, files in os.walk(db_path):
        job_id = path.split("/")[-1]

        for file in files:
            final_path = f'{abs_path}/{job_id}/{file}'
            if final_path.endswith('pass.xlsx'):
                if job_id not in res:
                    res[job_id] = {"downloadPaths": {}}
                res[job_id]["downloadPaths"]["green"] = final_path
            elif final_path.endswith('fail.xlsx'):
                if job_id not in res:
                    res[job_id] = {"downloadPaths": {}}
                res[job_id]["downloadPaths"]["blue"] = final_path
            elif final_path.endswith('.xlsx'):
                if job_id not in res:
                    res[job_id] = {"downloadPaths": {}}
                res[job_id]["downloadPaths"]["grey"] = final_path
    return res


@app.get("/hits")
async def get_history():
    db_path = './db'
    for _, dirs, _ in os.walk(db_path):
        return dirs
        break
