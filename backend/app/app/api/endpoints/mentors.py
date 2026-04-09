from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
# from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.get_allmentor import Getall_mentor
from backend.app.app.api.deps import get_db, role_required
from fastapi import Request
from backend.app.app.schemas.user_schema import MentorCreate, MentorUpdate, UserUpdate
from backend.app.app.crud.get_allmentor import Add_mentor

router = APIRouter(tags=["Mentor"])

@router.get("/get_all_mentors")
def get_mentors(db:Session = Depends(get_db),
    user = Depends(role_required([1, 2, 3, 4]))):
    try: 
        return Getall_mentor(db).get_all_mentors()
    except Exception as e:
        return {"error" : str(e)}
    
@router.post("/delete_mentor")
def delete_mentor(
    mentor_id: int,
    current_user = Depends(role_required([1])),
    db: Session = Depends(get_db)
):
    mentor_service = Getall_mentor(db)
    return mentor_service.delete_mentor(mentor_id)

@router.put("/update_mentor")
def update_mentor(
    mentor_id: int,
    payload: MentorUpdate,
    current_user = Depends(role_required([1])),
    db: Session = Depends(get_db)
):
    mentor_service = Getall_mentor(db)
    return mentor_service.update_mentor(mentor_id, payload)

@router.post("/add_mentor")
def add_mentor(
    mentor: MentorCreate,
    db: Session = Depends(get_db),
    user = Depends(role_required([1, 4]))
):
    try:
        result = Add_mentor(db).add_mentor(mentor)

        # custom error from CRUD
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
<<<<<<< HEAD
    


=======
>>>>>>> 42caf98b23bea226313c84c9f068bcb4e6dcd9cf
