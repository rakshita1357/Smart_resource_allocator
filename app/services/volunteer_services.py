from app.db.session import db

collection = db["volunteers"]

async def create_volunteer(data: dict):
    result = await collection.insert_one(data)
    return str(result.inserted_id)

async def get_all_volunteers():
    result = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        result.append(doc)
    return result