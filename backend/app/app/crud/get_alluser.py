from sqlalchemy.orm import Session
from backend.app.app.models import Users

class Getall_user:
    def __init__(self,db:Session):
        self.db=db

    def get_alluser(self):

        user = self.query(Users.username,
                          Users.email).all()
    
        return [row._asdict() for row in user]
    

