from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.get_allmentor import Getall_mentor
from backend.app.app.api.deps import get_db, role_required

router = APIRouter(tags=["Mentor"])

@router.get("/get_all_mentors")
def get_mentors(db:Session = Depends(get_db),
    user = Depends(role_required([1, 2, 3, 4]))):
    try: 
        return Getall_mentor(db).get_all_mentors()
    except Exception as e:
        return {"error" : str(e)}
