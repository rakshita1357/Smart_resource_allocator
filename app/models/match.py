from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from ..db.base import Base, TimestampMixin


class Match(Base, TimestampMixin):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"), nullable=False)
    need_id = Column(Integer, ForeignKey("needs.id"), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    status = Column(String, default="pending")

    volunteer = relationship("Volunteer", back_populates="matches")
    need = relationship("Need", back_populates="matches")

