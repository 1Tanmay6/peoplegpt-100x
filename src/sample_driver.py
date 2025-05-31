import json
import asyncio
from servers.resume_parser import ResumeParser, parse

from servers.connectors import OllamaConnector

ollama_connector = OllamaConnector(thinking='non-thinking')
rsp = ResumeParser(connector=ollama_connector)

# res = asyncio.run(
#     rsp.parse(r'/home/tanmaypatil/Documents/100x/Tanmay_Patil_CV.pdf'))

parse(r'/home/tanmaypatil/Documents/100x/Tanmay_Patil_CV.pdf')

# with open('./resume.json', 'w') as f:
#     json.dump(fp=f, obj=res, indent=4)
