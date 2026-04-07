from .session import SessionLocal, engine
from ..db.base import Base
from ..models.volunteer import Volunteer


def init_db():
    """Create tables and insert sample volunteers if none exist."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Volunteer).count()
        if existing == 0:
            samples = [
                Volunteer(name="Alice Smith", email="alice@example.com", phone="1234567890", latitude=12.9716, longitude=77.5946, skills=["medical", "first aid"], availability="immediate", experience_level="senior"),
                Volunteer(name="Bob Jones", email="bob@example.com", phone="2345678901", latitude=13.0827, longitude=80.2707, skills=["logistics", "transport"], availability="1 week", experience_level="mid"),
            ]
            db.add_all(samples)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Initialized DB with sample volunteers")

