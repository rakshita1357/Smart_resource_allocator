from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from ..db.base import Base, TimestampMixin


class Volunteer(Base, TimestampMixin):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    skills = Column(JSON, default=list)
    availability = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)

    # relationships
    matches = relationship("Match", back_populates="volunteer")

