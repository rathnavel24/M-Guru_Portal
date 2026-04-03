from sqlalchemy import Boolean, Column, DateTime, Integer, String, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class TimeLog(Base):
    __tablename__ = "timelog"

    time_log_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.task_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    start_time = Column(TIMESTAMP, default=func.now())
    end_time = Column(TIMESTAMP, default=func.now())
    total_time = Column(Integer)
    productive = Column(Boolean)
    status = Column(Integer)
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String)
    updated_at = Column(TIMESTAMP, default=func.now())

    task = relationship("Task", back_populates="tasktime")
    user = relationship("Users", back_populates="usertime")
