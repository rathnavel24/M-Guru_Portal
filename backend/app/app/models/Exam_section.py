from sqlalchemy import Column, DateTime, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Section(Base):

    __tablename__ = "exam_section"

    section_id = Column(Integer , primary_key=True)
    section_name = Column(String(100))

    question_section = relationship("Questions",back_populates="section")