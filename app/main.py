from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.volunteers import router as volunteer_router
from app.api.routes.ngos import router as ngo_router
from app.api.routes.matching import router as matching_router
from app.api.routes.survey_upload import router as survey_router

app = FastAPI(
    title="Smart Volunteer Matching System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular routers
app.include_router(volunteer_router)
app.include_router(ngo_router)
app.include_router(matching_router)
app.include_router(survey_router)


@app.get("/", tags=["Health"])
def root():
    """Root health endpoint indicating the API is running."""
    return {"message": "Smart Volunteer Matching API is running"}
# in process
