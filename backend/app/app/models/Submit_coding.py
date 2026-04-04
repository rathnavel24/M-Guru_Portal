from sqlalchemy import JSON, Column, Integer, TEXT, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class Coding_Submissions(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True)

    question_id = Column(Integer, ForeignKey("exam_questions.question_id"))
    user_id = Column(Integer, nullable=True)   # optional for now

    code = Column(TEXT)
    outputs = Column(JSON)
    passed = Column(Integer)
    total = Column(Integer)

    status = Column(String(20))  # PASS / FAIL

    created_at = Column(TIMESTAMP, server_default=func.now())