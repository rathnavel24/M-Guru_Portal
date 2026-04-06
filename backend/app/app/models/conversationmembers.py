from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class ConversationMember(Base):
    __tablename__ = "conversationmember"

    ConversationID = Column(Integer, ForeignKey("conversation.ConversationID"), primary_key=True)
    UserID = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    JoinedAt = Column(DateTime, default=func.now())
    Role = Column(String(20))
    status = Column(Integer, default=1)
    CreatedOn = Column(DateTime, default=func.now())
    CreatedBy = Column(String(100))
    updatedOn = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="members")
    user = relationship("Users", back_populates="conversation_memberships")

