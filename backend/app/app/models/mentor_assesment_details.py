from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from backend.app.app.db.base import Base

class AssessmentDetail(Base):
    __tablename__ = "assessment_details"

    id = Column(Integer, primary_key=True, index=True)

    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    obtained_marks = Column(Integer)
    task_details = Column(String)

    assessment = relationship("Assessment", back_populates="details")
    category = relationship("Category")