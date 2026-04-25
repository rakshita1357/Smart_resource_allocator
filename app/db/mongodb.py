import os
from importlib import import_module
from typing import Any

import certifi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found")

try:
    motor_asyncio = import_module("motor.motor_asyncio")
except ModuleNotFoundError:  # pragma: no cover - dependency guard
    motor_asyncio = None  # type: ignore[assignment]


class _UnavailableCollection:
    """Fallback collection that raises a clear error when used without Motor."""

    def __getattr__(self, name: str) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def create_index(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def find_one(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def insert_one(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def replace_one(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def update_one(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    async def delete_one(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")

    def find(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("MongoDB driver is not installed. Install project dependencies to enable database access.")


class _UnavailableDatabase:
    """Fallback database that returns collections which fail with a helpful message."""

    def __getitem__(self, name: str) -> _UnavailableCollection:
        return _UnavailableCollection()

    def __getattr__(self, name: str) -> _UnavailableCollection:
        return _UnavailableCollection()


if motor_asyncio is None:
    client = None
    db: Any = _UnavailableDatabase()
else:
    AsyncIOMotorClient = motor_asyncio.AsyncIOMotorClient
    client = AsyncIOMotorClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
    )
    db: Any = client["smart_resource_allocator"]


async def get_db() -> Any:
    """Return the shared MongoDB database instance."""
    return db
