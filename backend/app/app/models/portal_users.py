from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base



class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    type = Column(Integer,default=2)
    status = Column(Integer, default = 1)
    is2FA = Column(Boolean, default=False)
    batch = Column(Integer)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")

    # hari
    sent_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.from_id", back_populates="sender")

    received_emails = relationship(
        "Pay_email", foreign_keys="Pay_email.to_id", back_populates="receiver")

