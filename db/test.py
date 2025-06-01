import json
import duckdb

con = duckdb.connect(
    './db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb')
# print(con.execute("SELECT * FROM duplicate_resumes;").fetchall())
res = con.execute("SELECT id, raw FROM resumes;").fetchall()
for resume in res:
    id, raw = resume
    raw = json.loads(raw)
    print(type(raw))
    print({id: 70})
