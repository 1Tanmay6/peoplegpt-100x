from typing import Dict, Any
from ..groq_integration import GroqScorer


async def calculate_language_score(skill_data: dict) -> dict:
    """
    Calculate technical skills score using Groq API for dynamic evaluation
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Get current industry-standard scoring criteria
    criteria = await scorer.get_scoring_criteria('skills')

    # Get detailed analysis and scores
    analysis = await scorer.analyze_profile({'skill': skill_data}, 'skills')

    return {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100
    }
