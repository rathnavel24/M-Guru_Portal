from sqlalchemy import Boolean, Column, DateTime, Integer, String, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class PassLog(Base):
    __tablename__ = "passlog"

    pass_log_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.task_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    pass_time = Column(TIMESTAMP, default=func.now())
    resume_time = Column(TIMESTAMP, default=func.now())
    reason = Column(String)
    status = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String)
    updated_at = Column(TIMESTAMP, default=func.now())



    task = relationship("Task", back_populates="taskpass")
    user = relationship("Users", back_populates="userpass")
