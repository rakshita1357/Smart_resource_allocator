# Smart Volunteer Matching System

A modular FastAPI backend that accepts uploaded survey images, extracts text using OCR, identifies required skills, and matches needs with volunteers.

Quick start (development):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. (Optional) Install Tesseract OCR on your system and ensure `tesseract` is in PATH.

3. Run the app:

```powershell
uvicorn app.main:app --reload
```

Endpoints:
- POST /survey/upload - upload an image file
- POST /volunteers/ - create a volunteer
- GET /volunteers/ - list volunteers
- GET /match/need/{id} - get matches for a need

Notes:
- Uses SQLite by default for quick local testing. Set `DATABASE_URL` to a Postgres URL for production.
- OCR requires Tesseract installed on the host.

