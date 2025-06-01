from typing import Dict, Any
from ..groq_integration import GroqScorer


async def calculate_relevance_score(candidate_data: Dict[str, Any], job_requirements: Dict[str, Any] = None) -> dict:
    """
    Calculate relevance score using Groq API for dynamic evaluation
    If job_requirements provided, evaluates candidate specifically for that role
    Otherwise evaluates general industry relevance
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Get current relevance evaluation criteria
    criteria = await scorer.get_scoring_criteria('relevance')

    # Get detailed analysis and scores
    analysis = await scorer.analyze_profile(candidate_data, 'relevance', job_requirements)

    return {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100,
        'job_fit_analysis': analysis.get('job_fit_analysis') if job_requirements else None
    }
