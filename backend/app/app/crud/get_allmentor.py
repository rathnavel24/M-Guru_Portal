from sqlalchemy.orm import Session
from backend.app.app.models import Users
from backend.app.app.core.security import hash_password
from backend.app.app.schemas.user_schema import MentorUpdate, UserUpdate

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
            mentor.status = 0 
            self.db.commit()
            self.db.refresh(mentor)
            return {"message": "Mentor deactivated successfully"}
        else:
            return {"message": "Mentor not found"}
        
    def update_mentor(self, mentor_id: int, data: MentorUpdate):
        mentor = self.db.query(Users).filter(
            Users.user_id == mentor_id,
            Users.type == 4
        ).first()

        if not mentor:
            return {"message": "Mentor not found"}

        update_data = data.dict(exclude_unset=True) 

        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
            
        if mentor.status == 0:
          return {"message": "Inactive mentor cannot be updated"}

        for key, value in update_data.items():
            setattr(mentor, key, value)   

        self.db.commit()
        self.db.refresh(mentor)

        return {
            "message": "Mentor updated successfully",
            "updated_fields": list(update_data.keys())
        }
        
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
