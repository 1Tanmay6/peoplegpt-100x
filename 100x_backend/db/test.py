import json
import duckdb

con = duckdb.connect(
    '/home/tanmaypatil/Documents/100x/src/servers/extraction_server/db/resumes_82d4a9a2-3ecc-11f0-9f0a-9b4cd7206487.duckdb')
# print(con.execute("SELECT * FROM duplicate_resumes;").fetchall())
res = con.execute("SELECT * FROM resumes;").fetch_df()
print(res.to_excel('./test.xlsx'))
