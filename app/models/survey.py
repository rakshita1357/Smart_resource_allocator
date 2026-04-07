from sqlalchemy import Column, Integer, String, Text
from ..db.base import Base, TimestampMixin
from sqlalchemy.orm import relationship


class Survey(Base, TimestampMixin):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)

    needs = relationship("Need", back_populates="survey")

