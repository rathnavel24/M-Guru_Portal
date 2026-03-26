from sqlalchemy import Column, DateTime, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "exam_user"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(255))
    usertype = Column(String(20))
    Created_At = Column(DateTime, server_default=func.now())
    Updated_At = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_attempts = relationship("Attempts",back_populates="user")