import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Use check_same_thread only for SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Yield a database session for request and ensure it's closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

