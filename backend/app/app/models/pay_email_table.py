
from psycopg2 import Timestamp
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean, TIMESTAMP, Enum,DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Pay_email(Base):
    __tablename__ = "pay_email"


    id=Column(Integer,primary_key=True)
    invoice_no=Column(String)

    from_id=Column(Integer,ForeignKey('users.user_id'))
    to_id=Column(Integer,ForeignKey('users.user_id'))
    note=Column(Text)
    email_type=Column(String)
    amount=Column(Float)
    due_date = Column(TIMESTAMP) 
    account_name = Column(String, nullable=True)
    account_no = Column(String, nullable=True)
    ifsc = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    is_complete=Column(Boolean)
    status = Column(Integer, default=1)
    reference_no =Column(String(255))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")
    reminder_stage = Column(Integer, default=0)
    last_reminder_at = Column(DateTime, nullable=True)

    sender = relationship("Users", foreign_keys=[from_id], back_populates="sent_emails")
    receiver = relationship("Users", foreign_keys=[to_id], back_populates="received_emails")


