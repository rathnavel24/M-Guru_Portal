from sqlalchemy import Boolean, Column, DateTime, Integer, String, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "task"
    task_id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String(255))
    status = Column(Enum)
    start_time = Column(TIMESTAMP, default=func.now())
    completion_time = Column(TIMESTAMP, default=func.now())
    created_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100))
    updated_at = Column(TIMESTAMP, default=func.now())
    due_time = Column(TIMESTAMP, default=func.now())


    taskpass = relationship("PassLog", back_populates="task")
    user = relationship("Users", back_populates="usertask")
    tasktime = relationship("TimeLog", back_populates="task")













     