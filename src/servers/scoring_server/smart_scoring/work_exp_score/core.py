from datetime import datetime
from typing import Dict, Any, List
from ..groq_integration import GroqScorer


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    if not date_str or date_str.lower() == 'present':
        return datetime.now()
    try:
        return datetime.strptime(date_str, '%b %Y')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%B, %Y')
        except ValueError:
            return datetime.now()


def calculate_duration_months(from_date: str, to_date: str) -> float:
    """Calculate duration between two dates in months"""
    start_date = parse_date(from_date)
    end_date = parse_date(to_date)
    months = (end_date.year - start_date.year) * \
        12 + (end_date.month - start_date.month)
    return max(months, 0)


async def calculate_work_experience_score(work_experience: list) -> dict:
    """
    Calculate work experience score using Groq API for dynamic evaluation
    Returns a dictionary with score and detailed analysis
    """
    scorer = GroqScorer()

    # Get current work experience evaluation criteria
    criteria = await scorer.get_scoring_criteria('experience')

    # Get detailed analysis and scores
    analysis = await scorer.analyze_profile({'work_experience': work_experience}, 'experience')

    return {
        'score': analysis.get('score', 0),
        'breakdown': analysis.get('breakdown', {}),
        'reasoning': analysis.get('reasoning', {}),
        'criteria_used': criteria,
        'max_score': 100,
        'total_months': analysis.get('total_months', 0)
    }
