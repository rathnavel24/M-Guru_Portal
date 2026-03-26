
from psycopg2 import Timestamp
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean, TIMESTAMP, Enum,DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.app.db.base import Base


class Pay_email(Base):
    __tablename__ = "pay_email"


    id=Column(Integer,primary_key=True)
    invoice_no=Column(String,unique=True)

    from_id=Column(Integer,ForeignKey('users.user_id'))
    to_id=Column(Integer,ForeignKey('users.user_id'))
    note=Column(Text)
    email_type=Column(String)
    amount=Column(Float)
    due_date = Column(TIMESTAMP) 
    upi_id=Column(String)
    is_complete=Column(Boolean)
<<<<<<< HEAD
     
=======
    status = Column(Integer, default=1) 
>>>>>>> b0a0962f1b730e79bf1a83378244fdc10aa61212
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")


    sender = relationship("Users", foreign_keys=[from_id], back_populates="sent_emails")
    receiver = relationship("Users", foreign_keys=[to_id], back_populates="received_emails")


