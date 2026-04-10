from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    assessment_type_id = Column(Integer, ForeignKey("assessment_types.assessment_type_id"))

    category_name = Column(String)   # Task Delivery
    status = Column(Integer, default = 1)
    obtained_marks = Column(Integer) 
    total_marks = Column(Integer)
    # criteria = Column(String)       # Timely completion
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    

    assessment_type = relationship("AssessmentType", back_populates="categories")