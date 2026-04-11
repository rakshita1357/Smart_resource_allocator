from typing import List
from ..utils.skill_dictionary import SKILL_DICTIONARY


def extract_skills(tokens: List[str]) -> List[str]:
    """Extract skill categories from list of tokens using the skill dictionary.

    Returns a list of matched skill category names (unique).
    """
    if not tokens:
        return []

    matched = set()
    token_set = set(tokens)
    for category, keywords in SKILL_DICTIONARY.items():
        for kw in keywords:
            if kw.lower() in token_set:
                matched.add(category)
                break
    return list(matched)

# in process