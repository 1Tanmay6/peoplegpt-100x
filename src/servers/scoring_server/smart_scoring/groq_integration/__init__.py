import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
import groq
from ..config import ScoringConfig

load_dotenv()


class GroqScorer:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv('groq_api_key')
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY environment variable")

        self.client = groq.Client(api_key=self.api_key)
        # Updated to the model being actively used
        self.model = model or os.getenv("groq_model_name") or "gemma2-9b-it"

        # Define base prompts that can be customized by the LLM
        self._base_prompts = {
            'education': """
                As an expert in technical hiring, analyze this candidate's educational background. Consider:
                - Degree relevance to technology industry
                - Academic performance and rigor
                - Technical coursework and specializations
                - Additional certifications and continuous learning
                - Institution reputation in tech education
                
                Return a JSON object with these exact fields:
                {
                    "score": <number between 0-100>,
                    "breakdown": {
                        "degree_relevance": <score>,
                        "academic_performance": <score>,
                        "technical_coursework": <score>,
                        "certifications": <score>,
                        "institution_quality": <score>
                    },
                    "reasoning": {
                        "degree_relevance": "<explanation>",
                        "academic_performance": "<explanation>",
                        "technical_coursework": "<explanation>",
                        "certifications": "<explanation>",
                        "institution_quality": "<explanation>"
                    }
                }
                """,
            'skills': """
                As a technical expert, evaluate this candidate's skill set. Consider:
                - Skill relevance to current industry needs
                - Depth vs breadth of technical knowledge
                - Modern vs legacy technology balance
                - Framework and tool proficiency
                - Technical stack completeness
                
                Return a JSON object with these exact fields:
                {
                    "score": <number between 0-100>,
                    "breakdown": {
                        "industry_relevance": <score>,
                        "technical_depth": <score>,
                        "technology_balance": <score>,
                        "tool_proficiency": <score>,
                        "stack_completeness": <score>
                    },
                    "reasoning": {
                        "industry_relevance": "<explanation>",
                        "technical_depth": "<explanation>",
                        "technology_balance": "<explanation>",
                        "tool_proficiency": "<explanation>",
                        "stack_completeness": "<explanation>"
                    }
                }
                """,
            'projects': """
                As a senior technical evaluator, analyze these projects. Consider:
                - Technical complexity and scope
                - Problem-solving approach
                - Architecture and design decisions
                - Technology selection rationale
                - Implementation quality indicators
                - Impact and results achieved
                
                Return a JSON object with these exact fields:
                {
                    "score": <number between 0-100>,
                    "breakdown": {
                        "complexity": <score>,
                        "problem_solving": <score>,
                        "architecture": <score>,
                        "technology_choices": <score>,
                        "implementation": <score>,
                        "impact": <score>
                    },
                    "reasoning": {
                        "complexity": "<explanation>",
                        "problem_solving": "<explanation>",
                        "architecture": "<explanation>",
                        "technology_choices": "<explanation>",
                        "implementation": "<explanation>",
                        "impact": "<explanation>"
                    }
                }
                """,
            'experience': """
                As a technical hiring manager, evaluate this candidate's experience. Consider:
                - Relevance of roles to modern tech industry
                - Project complexity and impact
                - Growth in responsibilities
                - Technical diversity and adaptability
                - Modern tech stack exposure
                
                Return a JSON object with these exact fields:
                {
                    "score": <number between 0-100>,
                    "breakdown": {
                        "role_relevance": <score>,
                        "project_impact": <score>,
                        "growth_trajectory": <score>,
                        "technical_diversity": <score>,
                        "modern_tech_exposure": <score>
                    },
                    "reasoning": {
                        "role_relevance": "<explanation>",
                        "project_impact": "<explanation>",
                        "growth_trajectory": "<explanation>",
                        "technical_diversity": "<explanation>",
                        "modern_tech_exposure": "<explanation>"
                    }
                }
                """,
            'relevance': """
                As an industry expert, evaluate this candidate's overall profile. Consider:
                - Alignment with current tech industry needs
                - Career progression and growth potential
                - Technical capability and adaptability
                - Professional development indicators
                - Role suitability and readiness
                
                Return a JSON object with these exact fields:
                {
                    "score": <number between 0-100>,
                    "breakdown": {
                        "industry_alignment": <score>,
                        "growth_potential": <score>,
                        "technical_capability": <score>,
                        "professional_development": <score>,
                        "role_readiness": <score>
                    },
                    "reasoning": {
                        "industry_alignment": "<explanation>",
                        "growth_potential": "<explanation>",
                        "technical_capability": "<explanation>",
                        "professional_development": "<explanation>",
                        "role_readiness": "<explanation>"
                    }
                }
                """
        }

    async def analyze_profile(self, candidate_data: Dict[str, Any], aspect: str) -> Dict[str, Any]:
        aspect = ScoringConfig.validate_aspect(aspect)

        try:
            print(f"\nEvaluating {aspect}...")

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical hiring evaluator. Return a JSON object with score, breakdown, and reasoning fields."
                    },
                    {"role": "user",
                        "content": f"{self._base_prompts[aspect]}\n\nAnalyze this data:\n{json.dumps(candidate_data)}"}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=2000
            )

            content = chat_completion.choices[0].message.content
            # Truncated for readability
            print(f"Raw API Response for {aspect}:", content[:200] + "...")

            try:
                # Try to extract JSON from the response if it's embedded in text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = json.loads(content)

                # Validate and normalize the result
                if not isinstance(result.get('score'), (int, float)):
                    print(
                        f"Warning: Invalid score format in {aspect} response")
                    result['score'] = 0

                result['score'] = self._normalize_score(float(result['score']))

                if not isinstance(result.get('breakdown'), dict):
                    result['breakdown'] = {}
                if not isinstance(result.get('reasoning'), dict):
                    result['reasoning'] = {}

                print(f"Processed {aspect} score:", result['score'])
                return result

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON for {aspect}. Error: {str(e)}")
                print(f"Raw content: {content}")
                return {
                    'score': 0,
                    'breakdown': {},
                    'reasoning': {'error': f'Failed to parse LLM response: {str(e)}'}
                }

        except Exception as e:
            print(f"Error in {aspect} evaluation:", str(e))
            raise Exception(f"Error calling Groq API: {str(e)}")

    async def get_scoring_criteria(self, aspect: str) -> Dict[str, Any]:
        aspect = ScoringConfig.validate_aspect(aspect)

        try:
            print(f"\nGetting criteria for {aspect}...")

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in technical hiring evaluation criteria. Return a JSON object with scoring criteria and weights."
                    },
                    {"role": "user",
                        "content": f"Provide scoring criteria for {aspect}:\n{self._base_prompts[aspect]}"}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )

            content = chat_completion.choices[0].message.content
            # Truncated for readability
            print(
                f"Raw criteria response for {aspect}:", content[:200] + "...")

            try:
                # Try to extract JSON from the response if it's embedded in text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(
                    f"Failed to parse criteria JSON for {aspect}. Error: {str(e)}")
                return {"error": "Failed to parse LLM response", "raw_response": content}

        except Exception as e:
            print(f"Error getting criteria for {aspect}:", str(e))
            raise Exception(f"Error calling Groq API: {str(e)}")

    def _normalize_score(self, score: float) -> float:
        """Normalize score to be between 0 and MAX_SCORE"""
        return min(max(0, score), ScoringConfig.MAX_SCORE)
