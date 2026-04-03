# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Boolean, Column, Integer, TEXT, ForeignKey, TIMESTAMP
# from sqlalchemy.orm import relationship
# # from backend.app.app.models.Exam_questions import Questions
# from backend.app.app.db.base import Base

# class Conversations(Base):

#     __tablename__ = "conversations"
#     conversation_id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("portal_users.id"))
#     isGroup = Column(Boolean, default=False)
#     created_at = Column(TIMESTAMP)
#     updated_at = Column(TIMESTAMP)
#     created_by = Column(Integer, ForeignKey("portal_users.id"))

#     user = relationship("Users", foreign_keys=[user_id], back_populates="conversations")
#     creator = relationship("Users", foreign_keys=[created_by])