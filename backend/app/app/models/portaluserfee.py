from sqlalchemy import TIMESTAMP, Column, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from backend.app.app.db.base import Base


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    total_fee = Column(Float)
    paid_amount = Column(Float, default=0)
    status = Column(Integer, default = 1)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    created_by = Column(String(100), default="ADMIN")

    user = relationship("Users",back_populates="fees")
    tokens = relationship("Token", back_populates="user")