import os
import json
from dotenv import load_dotenv
from typing import Dict, Any
from ....connectors import GroqConnector
from typing_extensions import TypedDict
from ..config import ScoringConfig
load_dotenv()


class ScoringResult(TypedDict):
    # Education and skills evaluation
    education_score: float
    education_analysis: str
    skills_score: float
    skills_analysis: str
    language_score: float
    language_analysis: str
    # Experience and projects evaluation
    experience_score: float
    experience_analysis: str
    projects_score: float
    projects_analysis: str
    # Additional components
    relevance_score: float
    relevance_analysis: str


class GroqScorer:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv('groq_api_key')
        if not self.api_key:
            raise ValueError("Groq API key not found")
        self.connector = GroqConnector(api_key=self.api_key, model=model)

    async def evaluate_skills_education(self, education: list, skills: dict, requirements: dict) -> Dict:
        """Evaluate education and skills in a focused context with strict criteria"""
        prompt = """
        Perform a rigorous evaluation of education and skills (0-100). Be extremely critical and demanding:

        1. Education (Score strictly):
           - Evaluate not just degree level but also institution prestige and ranking
           - Consider grades/GPA (should be exceptional, >3.5 GPA or equivalent)
           - Assess relevance of coursework to required field
           - Look for additional certifications and continuing education
           - Penalize any gaps in education or incomplete degrees

        2. Technical Skills (High bar assessment):
           - Required skills must be demonstrated through concrete projects/work
           - Look for advanced/expert level proficiency
           - Value depth over breadth of knowledge
           - Check for modern versions/frameworks of technologies
           - Heavily penalize any missing required skills
           - Preferred skills should show mastery, not just familiarity

        3. Languages and Technologies (Critical evaluation):
           - Expect advanced proficiency in primary technologies
           - Look for evidence of system design and architecture skills
           - Check for patterns of continuous technological growth
           - Evaluate problem-solving capabilities demonstrated through tech choices
           - Penalize outdated or obsolete technology focus

        Guidelines for Scoring:
        - Score below 50 if any required skills are missing
        - Score below 70 unless candidate shows exceptional expertise
        - Only score above 80 for truly outstanding candidates
        - Maximum scores (90+) reserved for industry-leading expertise
        
        Keep analysis focused and brutally honest. Do not inflate scores.
        """

        context = {
            "education": education,
            "skills": skills,
            "requirements": {
                "education": requirements.get('required_education'),
                "required_skills": requirements.get('required_skills', []),
                "preferred_skills": requirements.get('preferred_skills', [])
            }
        }

        scorer = self.connector.create_obj(ScoringResult)
        return await self.connector.acall(scorer, f"{prompt}\n\nAnalyze:\n{json.dumps(context)}")

    async def evaluate_experience(self, experience: list, projects: list, requirements: dict) -> Dict:
        """Evaluate work experience, projects and relevance with stringent criteria"""
        prompt = """
        Perform a demanding evaluation of experience components (0-100). Be extremely critical:

        1. Professional Experience (Rigorous assessment):
           - Evaluate role progression and responsibility growth
           - Look for leadership and initiative in roles
           - Assess impact and measurable achievements
           - Consider company/organization prestige
           - Examine duration and stability in roles
           - Heavily penalize job-hopping or unexplained gaps
           - Look for evidence of mentoring and team leadership

        2. Projects (Complex technical evaluation):
           - Assess technical complexity and sophistication
           - Look for enterprise-scale implementations
           - Evaluate problem-solving depth
           - Consider business impact and ROI
           - Check for innovative approaches
           - Examine architecture and system design decisions
           - Penalize simple or academic-only projects

        3. Industry Relevance (Critical alignment):
           - Demand direct industry experience
           - Look for domain expertise and business understanding
           - Assess awareness of industry trends and challenges
           - Evaluate competitive landscape knowledge
           - Consider regulatory/compliance experience
           - Penalize industry switches or irrelevant experience

        Guidelines for Scoring:
        - Score below 50 if experience is primarily academic/internships
        - Score below 70 unless showing significant industry impact
        - Only score above 80 for proven industry leaders
        - Maximum scores (90+) reserved for exceptional industry veterans
        
        Be extremely selective and maintain high standards. Avoid score inflation.
        """

        context = {
            "experience": experience,
            "projects": projects,
            "requirements": {
                "min_years": requirements.get('min_experience_years', 0),
                "industry": requirements.get('industry_keywords', []),
                "role": requirements.get('job_title_keywords', [])
            }
        }

        scorer = self.connector.create_obj(ScoringResult)
        return await self.connector.acall(scorer, f"{prompt}\n\nAnalyze:\n{json.dumps(context)}")

    def calculate_final_score(self, skills_score: float, education_score: float,
                              experience_score: float, projects_score: float,
                              language_score: float, relevance_score: float) -> Dict:
        """Calculate final score with stricter thresholds"""
        weights = {
            'skills': 0.30,        # Increased weight for technical skills
            'education': 0.15,
            'experience': 0.25,
            'projects': 0.15,
            'language': 0.10,
            'relevance': 0.05      # Decreased weight for general relevance
        }

        final_score = (
            skills_score * weights['skills'] +
            education_score * weights['education'] +
            experience_score * weights['experience'] +
            projects_score * weights['projects'] +
            language_score * weights['language'] +
            relevance_score * weights['relevance']
        )

        # More stringent level determination
        if (experience_score >= 90 and skills_score >= 85 and
                language_score >= 85 and relevance_score >= 80):
            level = "senior"
        elif (experience_score >= 80 and skills_score >= 75 and
              language_score >= 75 and relevance_score >= 70):
            level = "mid"
        elif (experience_score >= 65 and skills_score >= 70):
            level = "junior"
        else:
            level = "entry"

        return {
            'final_score': final_score,
            'is_adequate': final_score >= 65,  # Increased threshold
            'recommended_level': level
        }

    async def evaluate_candidate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate candidate profile with all scoring components"""
        try:
            print("\nEvaluating candidate profile...")

            # First evaluation: Skills and Education
            skills_edu_result = await self.evaluate_skills_education(
                candidate_data.get('education', []),
                candidate_data.get('skill', {}),
                job_requirements
            )

            # Second evaluation: Experience, Projects and Relevance
            exp_result = await self.evaluate_experience(
                candidate_data.get('work_experience', []),
                candidate_data.get('projects', []),
                job_requirements
            )

            # Calculate final scores including language and relevance
            final_results = self.calculate_final_score(
                skills_edu_result.get('skills_score', 0),
                skills_edu_result.get('education_score', 0),
                exp_result.get('experience_score', 0),
                exp_result.get('projects_score', 0),
                # Added language score
                skills_edu_result.get('language_score', 0),
                exp_result.get('relevance_score', 0)  # Added relevance score
            )

            return {
                'final_score': final_results['final_score'],
                'is_adequate': final_results['is_adequate'],
                'recommended_level': final_results['recommended_level'],
                'breakdowns': {
                    'education': {
                        'score': skills_edu_result.get('education_score', 0),
                        'analysis': skills_edu_result.get('education_analysis', '')
                    },
                    'technical_skills': {
                        'score': skills_edu_result.get('skills_score', 0),
                        'analysis': skills_edu_result.get('skills_analysis', '')
                    },
                    'language_proficiency': {
                        'score': skills_edu_result.get('language_score', 0),
                        'analysis': skills_edu_result.get('language_analysis', '')
                    },
                    'work_experience': {
                        'score': exp_result.get('experience_score', 0),
                        'analysis': exp_result.get('experience_analysis', '')
                    },
                    'projects': {
                        'score': exp_result.get('projects_score', 0),
                        'analysis': exp_result.get('projects_analysis', '')
                    },
                    'industry_relevance': {
                        'score': exp_result.get('relevance_score', 0),
                        'analysis': exp_result.get('relevance_analysis', '')
                    }
                }
            }

        except Exception as e:
            print(f"Error in candidate evaluation:", str(e))
            raise Exception(f"Error in evaluation: {str(e)}")
