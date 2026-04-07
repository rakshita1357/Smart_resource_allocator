import os

try:
    import pytesseract
except Exception:  # pragma: no cover - pytesseract might not be installed in CI
    pytesseract = None


def extract_text(image_path: str) -> str:
    """Extract text from an image using OpenCV preprocessing and pytesseract.

    This function imports OpenCV lazily so the module can be imported even when
    OpenCV is not installed. If either OpenCV or pytesseract is missing, the
    function will return an empty string.
    """
    if not os.path.exists(image_path):
        return ""

    # Import cv2 lazily
    try:
        import cv2
    except Exception:
        # OpenCV not available
        return ""

    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return ""

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to binarize
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Optionally apply median blur to reduce noise
    processed = cv2.medianBlur(thresh, 3)

    if pytesseract is None:
        # If pytesseract missing, return empty but keep pipeline complete
        return ""

    # Run OCR
    text = pytesseract.image_to_string(processed)
    return text
