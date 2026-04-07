from math import radians, sin, cos, sqrt, atan2
from typing import Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lon points using the Haversine formula."""
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def availability_score(volunteer_availability: Optional[str], need_urgency: Optional[str]) -> float:
    """Return a simple availability match score between 0 and 1.

    This is a heuristic placeholder: returns 1 if availability matches urgency keywords, else 0.5.
    """
    if not volunteer_availability or not need_urgency:
        return 0.5
    v = volunteer_availability.lower()
    u = need_urgency.lower()
    if "immediate" in v or "hour" in v or "now" in v:
        if "high" in u or "urgent" in u:
            return 1.0
    if "week" in v and "low" in u:
        return 0.8
    return 0.6

