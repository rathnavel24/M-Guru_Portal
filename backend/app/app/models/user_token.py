from decimal import Decimal
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Numeric, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base



class Token(Base):
    __tablename__ = "token"

    token_id = Column(Integer,primary_key=True)
    token = Column(String)
    user_id = Column(Integer,ForeignKey('users.user_id'))
    login = Column(TIMESTAMP, )#default=func.now())
    logout = Column(TIMESTAMP)
    ideal_time=Column(Numeric(10, 2))
    last_activity = Column(TIMESTAMP, nullable=True)
    
    productive_minutes = Column(Float, default=0)
    status = Column(Integer)

    user = relationship("Users", back_populates="tokens")
   
