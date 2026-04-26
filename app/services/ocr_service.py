import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

try:
    import cv2
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    cv2 = None

try:
    import pytesseract
    from pytesseract import TesseractNotFoundError
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    pytesseract = None
    TesseractNotFoundError = RuntimeError


class OCRServiceError(RuntimeError):
    """Raised when OCR cannot be performed due to configuration or runtime issues."""


def _configure_tesseract() -> None:
    if pytesseract is None:
        raise OCRServiceError("pytesseract is not installed.")

    tesseract_cmd = (
        os.getenv("TESSERACT_CMD")
        or os.getenv("TESSERACT_PATH")
        or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_text(image_path: str) -> str:
    """Extract text from an image using OpenCV preprocessing and pytesseract."""
    _configure_tesseract()

    if cv2 is None:
        raise OCRServiceError("OpenCV is not installed. Install dependencies from requirements.txt.")

    if not Path(image_path).exists():
        raise OCRServiceError(f"Image file not found: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        raise OCRServiceError(f"Unable to read image file: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed = cv2.medianBlur(thresh, 3)

    try:
        return pytesseract.image_to_string(processed)
    except TesseractNotFoundError as exc:
        raise OCRServiceError(
            "Tesseract OCR is not installed or not in PATH. "
            "Install Tesseract and set TESSERACT_CMD to the executable path."
        ) from exc
    except Exception as exc:
        raise OCRServiceError(f"OCR extraction failed: {exc}") from exc
