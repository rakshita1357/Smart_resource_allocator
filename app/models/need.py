from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..db.base import Base, TimestampMixin


class Need(Base, TimestampMixin):
    __tablename__ = "needs"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    skills_required = Column(JSON, default=list)
    urgency_level = Column(String, nullable=True)
    people_affected = Column(Integer, nullable=True)

    survey = relationship("Survey", back_populates="needs")
    matches = relationship("Match", back_populates="need")

