from sqlalchemy import JSON, Column, Integer, String, TIMESTAMP, ForeignKey, TEXT
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Questions(Base):
    __tablename__ = "exam_questions"

    question_id = Column(Integer, primary_key=True)
    assessments_id = Column(Integer, ForeignKey("exam_assessments.assessment_id"))

    question_type = Column(String(255))
    question_text = Column(TEXT)
    question_section = Column(String(255))
    section_id = Column(Integer,ForeignKey("exam_section.section_id"))
    # correct_option = Column(String(1))

    assessment = relationship("Assessments", back_populates="que_assessment")
    user_questions = relationship("Options", back_populates="questions")
    section = relationship("Section",back_populates="question_section")
    attempt_question = relationship("Answers",back_populates="question")