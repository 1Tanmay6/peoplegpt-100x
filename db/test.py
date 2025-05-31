import duckdb

con = duckdb.connect(
    './db/resumes_3f496a1c-3e16-11f0-81c1-e1be77211e00.duckdb')
# print(con.execute("SELECT * FROM duplicate_resumes;").fetchall())
res = con.execute("SELECT * FROM resumes;").fetchall()
print(res[0])
