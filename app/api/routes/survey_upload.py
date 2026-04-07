from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
from typing import List
from app.db.session import get_db
from app.models.survey import Survey
from app.models.need import Need
from app.services.ocr_service import extract_text
from app.services.text_preprocessing import clean_text
from app.services.keyword_extractor import extract_skills

router = APIRouter(prefix="/survey", tags=["Survey"])

# storage path
DEFAULT_STORAGE = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "survey_images")
STORAGE_PATH = Path(os.getenv("SURVEY_STORAGE_DIR", DEFAULT_STORAGE)).expanduser().resolve()
if STORAGE_PATH.exists() and not STORAGE_PATH.is_dir():
    STORAGE_PATH = STORAGE_PATH.parent / (STORAGE_PATH.name + "_dir")
STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("/test")
def test_route():
    return {"message": "survey route working"}


@router.post("/upload")
async def upload_survey(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload an image, perform OCR and create a Need record."""
    if image.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"survey_{uuid.uuid4().hex}{ext}"
    file_path = str(STORAGE_PATH / filename)

    with open(file_path, "wb") as f:
        f.write(await image.read())

    # OCR
    extracted = extract_text(file_path)

    # Text processing
    tokens = clean_text(extracted)
    skills = extract_skills(tokens)

    # Persist Survey and Need
    survey = Survey(image_path=file_path, extracted_text=extracted)
    db.add(survey)
    db.commit()
    db.refresh(survey)

    need = Need(survey_id=survey.id, skills_required=skills)
    db.add(need)
    db.commit()
    db.refresh(need)

    return {"extracted_text": extracted, "skills_required": skills, "survey_id": survey.id, "need_id": need.id}
