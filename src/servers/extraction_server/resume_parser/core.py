import re
import docx
import fitz
from typing import Dict
from ...connectors import BaseConnector

from typing import List, TypedDict


class PersonalInformation(TypedDict):
    first_name: str
    last_name: str
    phone_number: str
    email_address: str
    linkedin_url: str
    website_url: str
    headline: str
    github_url: str


class Skill(TypedDict):
    category: str
    skill_values: List[str]


class WorkExperience(TypedDict):
    company_name: str
    job_title: str
    city: str
    country: str
    from_date: str
    to_date: str
    description: str


class Education(TypedDict):
    institution_name: str
    field_of_study: str
    degree: str
    grade: str
    city: str
    country: str
    from_date: str
    to_date: str
    description: str


class Certification(TypedDict):
    certification_name: str
    issuer: str
    certification_date: str
    certification_expiry_date: str
    certification_url: str
    description: str


class Summary(TypedDict):
    profile: str


class Achievements(TypedDict):
    achievements: str


class Project(TypedDict):
    title: str
    project_role: str
    city: str
    country: str
    from_date: str
    to_date: str
    description: str


class ResumeJSON(TypedDict):
    personal_information: PersonalInformation
    skill: Skill
    work_experience: List[WorkExperience]
    education: List[Education]
    certifications: List[Certification]
    summary: Summary
    achievements: Achievements
    projects: List[Project]


class ResumeParser:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.connector_obj = self.connector.create_obj(structure=ResumeJSON)

    async def parse(self, file_path: str) -> Dict:
        if file_path.endswith('.pdf'):
            text = self._extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

        formatted_data = await self.connector.acall(self.connector_obj, text+"\n\nPlease read all the text very thoroughly and make sure that all the fields are appropiatly filled.")
        return formatted_data

    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """
        Extracts text from each page in “blocks,” and returns one string that
        shows page and block boundaries. Better for when you want to see
        headings, paragraphs, etc. instead of a flat blob of text.
        """
        doc = fitz.open(file_path)
        pieces = []

        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            blocks = page.get_text("dict")["blocks"]

            pieces.append(f"[Page {page_number + 1}]\n")

            for bl in blocks:
                if bl["type"] != 0:
                    continue

                block_text = ""
                for line in bl["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += "\n"

                block_text = block_text.strip()
                if block_text:
                    pieces.append(block_text)
                    pieces.append("\n")

            pieces.append("\n")

        return "".join(pieces)

    @staticmethod
    def _extract_text_from_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
