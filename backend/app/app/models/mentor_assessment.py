from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    assessment_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    assessment_type_id = Column(Integer, ForeignKey("assessment_types.assessment_type_id"))

    intern_id = Column(Integer, ForeignKey("users.user_id"))
    mentor_id = Column(Integer, ForeignKey("users.user_id"))

    # category_id = Column(Integer, ForeignKey("categories.id"))

    # date = Column(Date)
    remarks = Column(String)
    task_details = Column(String,nullable=True)
    obtained_marks = Column(Integer, nullable=True)

    assessment_date = Column(Date, nullable=True)  

    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now())

    # intern = relationship("Users", foreign_keys=[intern_id])
    # mentor = relationship("Users", foreign_keys=[mentor_id])

    # scores = relationship("AssessmentScore", back_populates="assessment", cascade="all, delete")

    intern = relationship("Users",foreign_keys=[intern_id],back_populates="intern_assessments") 

    mentor = relationship("Users",foreign_keys=[mentor_id],back_populates="mentor_assessments")

    details = relationship("AssessmentDetail", back_populates="assessment")
    assessment_type=relationship("AssessmentType")

    # category = relationship("Category", back_populates="cat_assesment")

    # categories = relationship("Category", back_populates="assessment_type")
