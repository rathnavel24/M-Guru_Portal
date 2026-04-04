from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base

class Message(Base):
    __tablename__ = "message"

    MessageID = Column(Integer, primary_key=True)
    ConversationID = Column(Integer, ForeignKey("conversation.ConversationID"), nullable=False)
    SenderID = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    ReceiverID = Column(Integer, ForeignKey("users.user_id"))
    Content = Column(String(255))
    status = Column(Integer, default=1)
    CreatedOn = Column(DateTime, default=func.now())
    CreatedBy = Column(Integer)
    updatedOn = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("Users", foreign_keys=[SenderID], back_populates="messages_sent")
    receiver = relationship("Users", foreign_keys=[ReceiverID], back_populates="messages_received")