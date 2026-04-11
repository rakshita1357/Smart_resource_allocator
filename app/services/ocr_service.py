import os
import logging

try:
    import pytesseract
    from PIL import Image
except Exception:  # pragma: no cover - optional deps in some environments
    pytesseract = None
    Image = None


logger = logging.getLogger(__name__)


def extract_text(image_path: str) -> str:
    """Extract text from an image using Pillow + pytesseract with a safe fallback.

    This implementation uses Pillow to open the image and passes it to pytesseract.
    If pytesseract or Pillow are not available, returns an empty string but logs a warning.
    """
    if not os.path.exists(image_path):
        logger.warning("OCR: image path does not exist: %s", image_path)
        return ""

    if pytesseract is None or Image is None:
        logger.warning("OCR: pytesseract or Pillow not available.")
        return ""

    try:
        img = Image.open(image_path)
        # Optional: convert to grayscale to improve OCR
        img = img.convert("L")
        text = pytesseract.image_to_string(img)
        return text or ""
    except Exception as exc:
        logger.exception("OCR failed for %s: %s", image_path, exc)
        return ""
