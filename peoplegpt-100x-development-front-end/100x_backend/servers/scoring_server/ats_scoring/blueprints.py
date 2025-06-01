from dataclasses import dataclass
from typing import List


@dataclass
class ScoringWeights:
    """Configuration for scoring weights"""
    skills_match: float = 0.30
    experience_relevance: float = 0.25
    education_match: float = 0.15
    career_progression: float = 0.10
    project_relevance: float = 0.20
    recency: float = 0.05
    completeness: float = 0.05


@dataclass
class JobRequirements:
    """Job requirements for scoring"""
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: int
    required_education: str
    industry_keywords: List[str]
    job_title_keywords: List[str]
    extra_information: List[str]
    location_preference: str = ""
