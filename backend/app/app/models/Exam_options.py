from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, TEXT, Boolean,CHAR
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Options(Base):
    __tablename__ = "exam_options"

    option_id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("exam_questions.question_id"))
    option_label = Column(CHAR(1))
    option_text = Column(TEXT)
    is_correct = Column(Boolean)

    questions = relationship("Questions",back_populates="user_questions")

