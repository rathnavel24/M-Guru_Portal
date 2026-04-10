from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    Assessment_id = Column(Integer, primary_key=True, index=True)

    intern_id = Column(Integer, ForeignKey("users.user_id"))
    mentor_id = Column(Integer, ForeignKey("users.user_id"))

    # date = Column(Date)
    remarks = Column(String)
    task_details = Column(String,nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now())

    # intern = relationship("Users", foreign_keys=[intern_id])
    # mentor = relationship("Users", foreign_keys=[mentor_id])

    intern = relationship("Users",foreign_keys=[intern_id],back_populates="intern_assessments") 

    mentor = relationship("Users",foreign_keys=[mentor_id],back_populates="mentor_assessments")