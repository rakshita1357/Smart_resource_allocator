from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from pathlib import Path

from app.db.session import db
from app.services.ocr_service import OCRServiceError, extract_text
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
async def test_route():
    return {"message": "survey route working"}


@router.post("/upload")
async def upload_survey(image: UploadFile = File(...)):
    if not image.content_type or image.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    ext = os.path.splitext(image.filename or "")[1] or ".jpg"
    filename = f"survey_{uuid.uuid4().hex}{ext}"
    file_path = str(STORAGE_PATH / filename)

    with open(file_path, "wb") as f:
        f.write(await image.read())

    try:
        extracted = extract_text(file_path)
    except OCRServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    tokens = clean_text(extracted)
    skills = extract_skills(tokens)

    survey_col = db["surveys"]
    need_col = db["needs"]

    survey_doc = {
        "image_path": file_path,
        "extracted_text": extracted
    }
    survey_res = await survey_col.insert_one(survey_doc)
    survey_id = str(survey_res.inserted_id)

    need_doc = {
        "survey_id": survey_id,
        "skills_required": skills
    }
    need_res = await need_col.insert_one(need_doc)
    need_id = str(need_res.inserted_id)

    return {
        "extracted_text": extracted,
        "skills_required": skills,
        "survey_id": survey_id,
        "need_id": need_id
    }
