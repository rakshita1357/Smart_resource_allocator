import os


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")


def get_survey_storage_dir() -> str:
    return os.getenv("SURVEY_STORAGE_DIR", None)


APP_NAME = os.getenv("APP_NAME", "Smart Volunteer Matching System")
