from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, TEXT, ForeignKey
from sqlalchemy.orm import relationship
# from backend.app.app.models.Exam_questions import Questions
from backend.app.app.db.base import Base

class Coding_Questions(Base):

    __tablename__ = "coding_questions"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("exam_questions.question_id"))

    input_data = Column(TEXT)
    expected_output = Column(TEXT)
    is_hidden = Column(Boolean, default=False)
    question = relationship("Questions", back_populates="coding_question")