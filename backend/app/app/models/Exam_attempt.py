from sqlalchemy import Column, DateTime, Integer, String, TIMESTAMP, ForeignKey, TEXT, Boolean
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Attempts(Base):
    __tablename__ = "exam_attempts"

    attempt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("exam_user.user_id"))
    assessment_id = Column(Integer, ForeignKey("exam_assessments.assessment_id"))
    # assessment_id = Column(Integer, autoincrement=True)
    started_at = Column(TIMESTAMP, default=func.now())
    submitted_at = Column(TIMESTAMP,nullable=True)

    aptitude_score = Column(Integer)
    technical_score = Column(Integer)
    total_score = Column(Integer)
    total_percentage = Column(Integer)
    status = Column(String)
    aptitude_correct = Column(Integer, default=0)
    aptitude_wrong = Column(Integer, default=0)
    aptitude_skipped = Column(Integer, default=0)

    technical_correct = Column(Integer, default=0)
    technical_wrong = Column(Integer, default=0)
    technical_skipped = Column(Integer, default=0)

    user = relationship("ExamUsers",back_populates="user_attempts")
    att_assessment = relationship("Assessments",back_populates="user_assessments")
    attempt_answer = relationship("Answers",back_populates="answer")