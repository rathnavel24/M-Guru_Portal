from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, TEXT, Boolean
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Attempts(Base):
    __tablename__ = "exam_attempts"

    attempt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    assessment_id = Column(Integer, ForeignKey("exam_assessments.assessment_id"))
    started_at = Column(TIMESTAMP, default=func.now())
    submitted_at = Column(TIMESTAMP, default=func.now())
    score = Column(Integer)
    percentage = Column(Integer)
    status = Column(String)

    user = relationship("Users",back_populates="user_attempts")
    att_assessment = relationship("Assessments",back_populates="user_assessments")
    attempt_answer = relationship("Answers",back_populates="answer")