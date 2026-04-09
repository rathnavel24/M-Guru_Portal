from sqlalchemy.orm import Session
from backend.app.app.models import Users

class Getall_mentor:
    def __init__(self,db:Session):
        self.db = db

    def get_all_mentors(self):
        return self.db.query(Users).filter(Users.type ==4).all()
    
    
    def delete_mentor(self, mentor_id: int):
        mentor = self.db.query(Users).filter(
            Users.user_id == mentor_id,
            Users.type == 4
        ).first()

        if mentor:
            self.db.delete(mentor)
            self.db.commit()
            return {"message": "Mentor deleted successfully"}
        else:
            return {"message": "Mentor not found"}