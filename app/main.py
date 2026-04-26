from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.matching import router as matching_router
from app.api.routes.ngos import router as ngo_router
from app.api.routes.survey_upload import router as survey_router
from app.api.routes.volunteers import router as volunteer_router
from app.db.mongodb import client, db as mongo_db
from app.services.auth_service import ensure_auth_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify MongoDB Atlas connectivity and initialize indexes on startup."""
    if client is None:
        print("MongoDB client is unavailable; skipping startup ping and index initialization.")
        yield
        return

    try:
        await client.admin.command("ping")
        print("MongoDB Atlas connected")
        await ensure_auth_indexes(mongo_db)
    except Exception as exc:
        print(f"MongoDB Atlas connection failed: {exc}")
    yield


app = FastAPI(
    title="Smart Volunteer Matching System",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include modular routers
app.include_router(auth_router)
app.include_router(volunteer_router)
app.include_router(ngo_router)
app.include_router(matching_router)
app.include_router(survey_router)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Root health endpoint indicating the API is running."""
    return {"message": "Smart Volunteer Matching API is running"}
