from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at timestamp to models."""

    created_at = Column(DateTime, default=datetime.utcnow)

