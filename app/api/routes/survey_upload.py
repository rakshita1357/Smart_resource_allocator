from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
import os
import uuid
from pathlib import Path
from app.db.mongodb import get_db
from app.services.ocr_service import extract_text
from app.services.text_preprocessing import clean_text
from app.services.keyword_extractor import extract_skills
import shutil
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/survey", tags=["Survey"])

# storage path - configurable via environment
DEFAULT_STORAGE = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "survey_images")
STORAGE_PATH = Path(os.getenv("SURVEY_STORAGE_DIR", DEFAULT_STORAGE)).expanduser().resolve()
if STORAGE_PATH.exists() and not STORAGE_PATH.is_dir():
    STORAGE_PATH = STORAGE_PATH.parent / (STORAGE_PATH.name + "_dir")
STORAGE_PATH.mkdir(parents=True, exist_ok=True)


@router.get("/test")
def test_route():
    return {"message": "survey route working"}


@router.post("/upload")
async def upload_survey(
    file: UploadFile = File(...),
    db=Depends(get_db),
):
    """Upload an image file, run OCR, extract skills and create Survey and Need documents in MongoDB."""
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image")

    # Save file
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"survey_{uuid.uuid4().hex}{ext}"
    file_path = str(STORAGE_PATH / filename)

    try:
        # Use shutil to stream file to disk safely
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        logger.exception("Failed saving uploaded file: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save uploaded file")
    finally:
        await file.close()

    # Run OCR (sync)
    try:
        extracted = extract_text(file_path)
    except Exception as exc:
        logger.exception("OCR processing failed: %s", exc)
        extracted = ""

    # Text processing
    tokens = clean_text(extracted)
    skills = extract_skills(tokens)

    # Persist Survey and Need
    try:
        survey_doc = {"image_path": file_path, "extracted_text": extracted}
        survey_result = await db.surveys.insert_one(survey_doc)
        survey_id = str(survey_result.inserted_id)

        need_doc = {
            "survey_id": survey_id,
            "skills_required": skills,
            "urgency_level": None,
            "location": None,
        }
        need_result = await db.needs.insert_one(need_doc)
        need_id = str(need_result.inserted_id)
    except Exception as exc:
        logger.exception("DB persist failed: %s", exc)
        # Attempt cleanup of saved file to avoid orphaned files
        try:
            os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist survey data")

    return {
        "filename": filename,
        "extracted_text": extracted,
        "skills_detected": skills,
        "survey_id": survey_id,
        "need_id": need_id,
    }
