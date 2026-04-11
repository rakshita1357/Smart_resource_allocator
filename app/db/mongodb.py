import os
import importlib
from typing import AsyncGenerator, Any, Dict, List
from dotenv import load_dotenv
import uuid

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "smart_volunteer_db")

_client = None
_db = None

# Try to use motor if available
try:
    motor = importlib.import_module("motor.motor_asyncio")
    AsyncIOMotorClient = getattr(motor, "AsyncIOMotorClient")
    _client = AsyncIOMotorClient(MONGO_URL)
    _db = _client[DB_NAME]
except Exception:
    _client = None
    _db = None


class _InsertOneResult:
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class _InMemoryCollection:
    def __init__(self):
        self._docs: List[Dict[str, Any]] = []

    async def insert_one(self, doc: Dict[str, Any]):
        new_doc = dict(doc)
        new_id = uuid.uuid4().hex
        new_doc["id"] = new_id
        # also keep _id key for some code paths
        new_doc["_id"] = new_id
        self._docs.append(new_doc)
        return _InsertOneResult(new_id)

    async def find_one(self, filter: Dict[str, Any]):
        if not filter:
            return self._docs[0] if self._docs else None
        for d in self._docs:
            matched = True
            for k, v in filter.items():
                # support _id and id matching
                if k == "_id" or k == "id":
                    if str(d.get("_id") or d.get("id")) != str(v):
                        matched = False
                        break
                else:
                    if d.get(k) != v:
                        matched = False
                        break
            if matched:
                return d
        return None

    def find(self, filter: Dict[str, Any] = None):
        # return object with to_list
        docs = []
        if not filter:
            docs = list(self._docs)
        else:
            for d in self._docs:
                matched = True
                for k, v in filter.items():
                    if k == "_id" or k == "id":
                        if str(d.get("_id") or d.get("id")) != str(v):
                            matched = False
                            break
                    else:
                        if d.get(k) != v:
                            matched = False
                            break
                if matched:
                    docs.append(d)

        class _Cursor:
            def __init__(self, docs_list: List[Dict[str, Any]]):
                self._docs = docs_list

            async def to_list(self, length: int) -> List[Dict[str, Any]]:
                return list(self._docs[:length])

        return _Cursor(docs)


class _InMemoryDB:
    def __init__(self):
        self.volunteers = _InMemoryCollection()
        self.ngos = _InMemoryCollection()
        self.surveys = _InMemoryCollection()
        self.needs = _InMemoryCollection()
        self.matches = _InMemoryCollection()


_inmemory_db = _InMemoryDB()

async def get_db() -> AsyncGenerator:
    """Yield the Motor DB instance or an in-memory fallback for tests.

    This allows the app to run without a live MongoDB during development/tests.
    """
    if _db is not None:
        yield _db
        return
    # fallback to in-memory DB
    yield _inmemory_db
    return
