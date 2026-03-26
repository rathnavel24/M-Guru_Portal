from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base
from backend.app.app.models.enums import user_activity_enum,user_role_enum



class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    type = Column(user_role_enum, default="student")
    status = Column(user_activity_enum, default="active")
    is2FA = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")

    # hari
    sent_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.from_id", back_populates="sender")

    received_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.to_id", back_populates="receiver")
    
    #koushi
    user_attempts = relationship("Attempts",back_populates="user")
