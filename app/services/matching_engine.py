from app.db.session import db
from app.utils.location_utils import haversine_distance, availability_score

def _jaccard_similarity(a, b):
    set_a = set([x.lower() for x in a])
    set_b = set([x.lower() for x in b])
    if not set_a and not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _distance_score(lat1, lon1, lat2, lon2):
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    if dist == float("inf"):
        return 0.0
    return max(0.0, 1 - (dist / 200))


async def match_volunteers(need_id: str, top_k: int = 10):
    needs_col = db["needs"]
    vol_col = db["volunteers"]
    match_col = db["matches"]

    need = await needs_col.find_one({"_id": need_id})
    if not need:
        return []

    volunteers = vol_col.find()

    results = []

    async for vol in volunteers:
        skill_score = _jaccard_similarity(
            vol.get("skills", []),
            need.get("skills_required", [])
        )

        dist_score = _distance_score(
            vol.get("latitude"),
            vol.get("longitude"),
            need.get("latitude"),
            need.get("longitude"),
        )

        avail = availability_score(
            vol.get("availability"),
            need.get("urgency_level")
        )

        score = 0.6 * skill_score + 0.2 * dist_score + 0.2 * avail

        match_doc = {
            "volunteer_id": str(vol["_id"]),
            "need_id": need_id,
            "score": score,
            "status": "pending"
        }

        res = await match_col.insert_one(match_doc)

        results.append({
            "match_id": str(res.inserted_id),
            "volunteer": {
                "id": str(vol["_id"]),
                "name": vol.get("name"),
                "email": vol.get("email"),
                "skills": vol.get("skills"),
            },
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# in process