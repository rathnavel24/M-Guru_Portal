from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class AssessmentType(Base):
    __tablename__ = "assessment_types"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessment.assessment_id"))
    assessment_name = Column(String)  # Technical / Presentation / Soft Skills
    status = Column(Integer, default = 1)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now())

    categories = relationship("Category", back_populates="assessment_type")