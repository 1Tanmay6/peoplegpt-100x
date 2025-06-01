from ..groq_integration import GroqScorer


async def calculate_education_score(education_data: list, job_requirements: dict = None) -> dict:
    """
    Calculate education score using Groq API for dynamic evaluation
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Get current scoring criteria
    criteria = await scorer.get_scoring_criteria('education')

    # Get detailed analysis and scores
    analysis = await scorer.analyze_profile({'education': education_data}, 'education', job_requirements)

    return {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100
    }
