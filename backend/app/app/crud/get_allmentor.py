from sqlalchemy.orm import Session
from backend.app.app.models import Users

class Getall_mentor:
    def __init__(self,db:Session):
        self.db = db

    def get_all_mentors(self):
        return self.db.query(Users).filter(Users.type ==4).all()