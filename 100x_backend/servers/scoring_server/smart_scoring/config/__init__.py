import json
import os

"""
Configuration module for the scoring system.
Now uses Grok API for dynamic scoring criteria instead of static configurations.
"""


class ScoringConfig:
    """Base configuration for scoring system"""
    MAX_SCORE = 100
    ADEQUACY_THRESHOLD = 60

    # Role levels for reference only - actual evaluation done by Grok
    ROLE_LEVELS = ['entry', 'junior', 'mid', 'senior']

    # Scoring aspects
    ASPECTS = [
        'education',
        'experience',
        'skills',
        'projects',
        'relevance'
    ]

    @staticmethod
    def validate_role_level(role_level: str) -> str:
        """Validate and normalize role level input"""
        role_level = role_level.lower()
        if role_level not in ScoringConfig.ROLE_LEVELS:
            return 'entry'  # Default to entry level if invalid
        return role_level

    @staticmethod
    def validate_aspect(aspect: str) -> str:
        """Validate scoring aspect"""
        aspect = aspect.lower()
        if aspect not in ScoringConfig.ASPECTS:
            raise ValueError(
                f"Invalid scoring aspect. Must be one of: {', '.join(ScoringConfig.ASPECTS)}")
        return aspect


def load_config(config_name: str) -> dict:
    """
    Load configuration from JSON file
    config_name: Name of the config file without .json extension
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, f"{config_name}.json")

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Configuration file {config_name}.json not found")
    except json.JSONDecodeError:
        raise ValueError(
            f"Invalid JSON in configuration file {config_name}.json")
