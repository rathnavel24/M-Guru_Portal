from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class Conversation(Base):
    __tablename__ = "conversation"

    ConversationID = Column(Integer, primary_key=True)
    Name = Column(String(100))
    IsGroup = Column(Boolean, default=True)
    status = Column(Integer, default=1)

    # Link batch to Users.batch
    batch = Column(Integer, ForeignKey("users.batch"))
    
    CreatedOn = Column(DateTime, default=func.now())
    CreatedBy = Column(String(100))
    updatedOn = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    members = relationship("ConversationMember", back_populates="conversation", cascade="all, delete-orphan")