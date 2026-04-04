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
    current_task_id = Column(Integer)    #new add
    type = Column(Integer, default=2)
    status = Column(Integer, default=1)
    is2FA = Column(Boolean, default=False)
    batch = Column(Integer)
    phone = Column(String)
    tech_stack = Column(String)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")

    fees = relationship("Fee", back_populates="user", cascade="all, delete-orphan")
    sent_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.from_id", back_populates="sender"
    )

    received_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.to_id", back_populates="receiver"
    )

    tokens = relationship("Token", back_populates="user")
    conversations = relationship("Conversations", back_populates="user")
    created_conversations = relationship("Conversations", foreign_keys="Conversations.created_by", back_populates="creator")

    userpass= relationship("PassLog", back_populates="user")
    usertask = relationship("Task", back_populates="user")
    usertime = relationship("TimeLog", back_populates="user")
