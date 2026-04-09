from sqlalchemy.orm import Session
from backend.app.app.models import Users
from backend.app.app.core.security import hash_password

class Getall_mentor:
    def __init__(self,db:Session):
        self.db = db

    def get_all_mentors(self):
        return self.db.query(Users).filter(Users.type ==4).all()
    

class Add_mentor:
    def __init__(self, db: Session):
        self.db = db

    def add_mentor(self, data):

        existing = self.db.query(Users).filter(Users.email == data.email).first()
        if existing:
            return {"error": "Email already exists"}

        hashed_password = hash_password(data.password)

        new_mentor = Users(
            username=data.username,
            email=data.email,
            password=hashed_password,
            batch=data.batch if data.batch is not None else 0,
            phone=data.phone,
            tech_stack=data.tech_stack,
            type=4,
            status=1,
            # created_by=user_obj.username
            created_by="ADMIN"
        )

        self.db.add(new_mentor)
        self.db.commit()
        self.db.refresh(new_mentor)

        return {
            "message": "Mentor added successfully",
            "mentor_id": new_mentor.user_id,
            "created_by": new_mentor.created_by
        }