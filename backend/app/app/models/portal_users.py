from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(255))
    password = Column(String(255))
    current_task_id = Column(Integer)
    type = Column(Integer, default=2)
    status = Column(Integer, default=1)
    is2FA = Column(Boolean, default=False)
    batch = Column(Integer)
    phone = Column(String)
    tech_stack = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), default="ADMIN")

    # Relationships
    fees = relationship("Fee", back_populates="user", cascade="all, delete-orphan")
    sent_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.from_id", back_populates="sender"
    )
    received_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.to_id", back_populates="receiver"
    )
    tokens = relationship("Token", back_populates="user")
    userpass = relationship("PassLog", back_populates="user")
    usertask = relationship("Task", back_populates="user")
    usertime = relationship("TimeLog", back_populates="user")

    # Messaging relationships
    messages_sent = relationship(
        "Message",
        foreign_keys="Message.SenderID",
        back_populates="sender"
    )
    messages_received = relationship(
        "Message",
        foreign_keys="Message.ReceiverID",
        back_populates="receiver"
    )
    conversation_memberships = relationship(
        "ConversationMember",
        back_populates="user"
    )
    conversations = relationship(
        "Conversation",
        back_populates="user_batch",
        foreign_keys="Conversation.batch"
    )

