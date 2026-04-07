from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"))  # intern
    assigned_to = Column(Integer, ForeignKey("users.user_id"))  # admin/mentor

    category = Column(String(100))
    message = Column(Text)
    reply = Column(Text, nullable=True)

    status = Column(String(50), default="pending")  # pending/replied/resolved

    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())