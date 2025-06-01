from datetime import datetime
from typing import Dict, Any
from ..groq_integration import GroqScorer


async def calculate_experience_adequacy(candidate_data: Dict[str, Any], job_requirements: dict = None, role_level: str = 'entry') -> dict:
    """
    Calculate if candidate's experience is adequate using Groq API for dynamic evaluation
    role_level options: 'entry', 'junior', 'mid', 'senior'
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Add role level to the analysis context
    analysis_context = {
        'work_experience': candidate_data.get('work_experience', []),
        'projects': candidate_data.get('projects', []),
        'skill': candidate_data.get('skill', {}),
        'certifications': candidate_data.get('certifications', [])
    }

    # Get current experience evaluation criteria
    criteria = await scorer.get_scoring_criteria('experience')

    # Get detailed analysis and scores, passing job requirements
    analysis = await scorer.analyze_profile(analysis_context, 'experience', job_requirements)

    result = {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100,
        # Using 70 as default threshold
        'is_adequate': analysis.get('score', 0) >= 70,
        'recommended_level': analysis.get('recommended_level', role_level)
    }

    return result


def _calculate_total_months(work_experience: list) -> int:
    """Calculate total months of experience from work history"""
    total_months = 0

    for exp in work_experience:
        from_date = exp.get('from_date', '')
        to_date = exp.get('to_date', 'Present')

        if from_date:
            try:
                start_date = datetime.strptime(from_date, '%b %Y')
                end_date = datetime.now() if to_date == 'Present' else datetime.strptime(to_date, '%b %Y')
                months = (end_date.year - start_date.year) * \
                    12 + (end_date.month - start_date.month)
                total_months += max(0, months)
            except ValueError:
                pass

    return total_months


def _get_recommended_level(total_months: int, score: float, config: dict) -> str:
    """Determine recommended experience level based on months and score"""
    adequacy_threshold = config['adequacy_threshold']

    if score < adequacy_threshold:
        return None

    for level, reqs in reversed(config['role_levels'].items()):
        if total_months >= reqs['min_experience']:
            return level

    return 'entry'
