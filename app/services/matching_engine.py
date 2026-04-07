from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.volunteer import Volunteer
from ..models.need import Need
from ..models.match import Match
from ..utils.location_utils import haversine_distance, availability_score


def _jaccard_similarity(a: List[str], b: List[str]) -> float:
    set_a = set([x.lower() for x in a])
    set_b = set([x.lower() for x in b])
    if not set_a and not set_b:
        return 0.0
    inter = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(inter) / len(union) if union else 0.0


def _distance_score(lat1, lon1, lat2, lon2) -> float:
    dist_km = haversine_distance(lat1, lon1, lat2, lon2)
    if dist_km == float("inf"):
        return 0.0
    # Convert to score: distance 0 -> 1, >200 km -> 0
    score = max(0.0, 1 - (dist_km / 200.0))
    return score


def match_volunteers(db: Session, need_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
    """Find and store matches for a given need.

    Returns list of top matched volunteers with score and volunteer info.
    """
    need = db.query(Need).filter(Need.id == need_id).first()
    if not need:
        return []

    volunteers = db.query(Volunteer).all()
    results = []

    for vol in volunteers:
        # Skill similarity (60%)
        skill_score = _jaccard_similarity(getattr(vol, "skills", []) or [], getattr(need, "skills_required", []) or [])

        # Distance score (20%)
        dist_score = _distance_score(getattr(vol, "latitude", None), getattr(vol, "longitude", None), getattr(need, "latitude", None), getattr(need, "longitude", None))

        # Availability score (20%)
        avail = availability_score(getattr(vol, "availability", None), getattr(need, "urgency_level", None))

        score = 0.6 * skill_score + 0.2 * dist_score + 0.2 * avail

        # Store match
        match = Match(volunteer_id=int(getattr(vol, "id")), need_id=int(getattr(need, "id")), score=score, status="pending")
        db.add(match)
        db.commit()
        db.refresh(match)

        results.append({
            "volunteer": {
                "id": getattr(vol, "id"),
                "name": getattr(vol, "name"),
                "email": getattr(vol, "email"),
                "skills": getattr(vol, "skills"),
                "latitude": getattr(vol, "latitude"),
                "longitude": getattr(vol, "longitude"),
                "availability": getattr(vol, "availability"),
            },
            "score": score,
            "match_id": getattr(match, "id"),
        })

    # Sort by score desc and return top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
