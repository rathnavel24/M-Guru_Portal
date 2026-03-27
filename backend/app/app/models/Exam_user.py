from sqlalchemy import Column, DateTime, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum



class ExamUsers(Base):
    __tablename__ = "exam_user"

    user_id = Column(Integer, primary_key=True , index=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))
    name = Column(String(100))
    email = Column(String(250))
    Created_At = Column(DateTime, server_default=func.now())
    Updated_At = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_attempts = relationship("Attempts",back_populates="user")