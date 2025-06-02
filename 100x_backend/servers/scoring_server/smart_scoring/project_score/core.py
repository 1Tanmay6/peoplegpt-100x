from typing import Dict, Any, List
from ..groq_integration import GroqScorer


async def calculate_project_score(projects: list, job_requirements: dict = None) -> dict:
    """
    Calculate project score using Groq API for dynamic evaluation
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Get current project evaluation criteria
    criteria = await scorer.get_scoring_criteria('projects')

    # Get detailed analysis and scores
    analysis = await scorer.analyze_profile({'projects': projects}, 'projects', job_requirements)

    return {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100
    }
