from typing import List, Dict, Any
from ..utils.location_utils import haversine_distance, availability_score


def _jaccard_similarity(a: List[str], b: List[str]) -> float:
    set_a = set([x.lower() for x in (a or [])])
    set_b = set([x.lower() for x in (b or [])])
    if not set_a and not set_b:
        return 0.0
    inter = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(inter) / len(union) if union else 0.0


def _distance_score(lat1, lon1, lat2, lon2) -> float:
    try:
        dist_km = haversine_distance(lat1, lon1, lat2, lon2)
    except Exception:
        return 0.0
    if dist_km == float("inf"):
        return 0.0
    score = max(0.0, 1 - (dist_km / 200.0))
    return score


async def match_volunteers(db, need_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Find and store matches for a given need id using MongoDB collections.

    Returns list of top matched volunteers with score and volunteer info.
    """
    need = await db.needs.find_one({"_id": need_id})
    # support case when need stored with string id in field 'id' or with _id ObjectId
    if need is None:
        need = await db.needs.find_one({"id": str(need_id)})
    if need is None:
        # attempt to find by string _id
        need = await db.needs.find_one({"_id": need_id})
    if need is None:
        return []

    need_skills = need.get("skills_required") or []
    need_lat = need.get("latitude")
    need_lon = need.get("longitude")
    need_urgency = need.get("urgency_level")

    volunteers = await db.volunteers.find().to_list(length=1000)
    results = []

    for vol in volunteers:
        skill_score = _jaccard_similarity(vol.get("skills", []), need_skills)
        dist_score = _distance_score(vol.get("latitude"), vol.get("longitude"), need_lat, need_lon)
        avail = availability_score(vol.get("availability"), need_urgency)
        score = 0.6 * skill_score + 0.2 * dist_score + 0.2 * avail

        # store match doc
        match_doc = {
            "volunteer_id": str(vol.get("_id") or vol.get("id")),
            "need_id": str(need.get("_id") or need.get("id") or need_id),
            "score": score,
            "status": "pending",
        }
        inserted = await db.matches.insert_one(match_doc)
        match_id = str(inserted.inserted_id)

        results.append({
            "volunteer": {
                "id": str(vol.get("_id") or vol.get("id")),
                "name": vol.get("name"),
                "email": vol.get("email"),
                "skills": vol.get("skills"),
                "latitude": vol.get("latitude"),
                "longitude": vol.get("longitude"),
                "availability": vol.get("availability"),
            },
            "score": score,
            "match_id": match_id,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
