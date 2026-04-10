from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    assessment_type_id = Column(Integer, ForeignKey("assessment_types.id"))

    category_name = Column(String)   # Task Delivery
    # criteria = Column(String)       # Timely completion
    status = Column(Integer, default = 1)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now())
    

    assessment_type = relationship("AssessmentType", back_populates="categories")