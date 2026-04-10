from fastapi import APIRouter, Depends
from requests import session
from sqlalchemy.orm import Session
from backend.app.app.crud.attendance import Attendance ,Check
from backend.app.app.api.deps import get_db, role_required

router = APIRouter(tags=["Attendance"])


@router.post("/viewbyadmin")
async def view(
    user_id: int,
    current_user=Depends(role_required([1])),
    db: Session = Depends(get_db),
):

    return Attendance(db).attendance(user_id)


@router.post("/viewbyuser")
async def view(current_user=Depends(role_required([1,2])), db: Session = Depends(get_db)):
    user_id = current_user.get("user_id")
    #print(user_id)
    return Attendance(db).attendance(user_id)


@router.post("/Check-in")
async def checkin(current_user=Depends(role_required([1,2])), db: Session = Depends(get_db)):
    return Check(db).checkin(current_user)


@router.post("/check-out")
async def checkout(current_user=Depends(role_required([1,2])), db: Session = Depends(get_db)):
    user_id=current_user.get("user_id")
    return Check(db).checkout(user_id)

@router.post("/user_status")
async def check(current_user=Depends(role_required([1,2])), db: Session = Depends(get_db)):
    #print("this from api status",current_user.get("user_id"))
    return Check(db).status(current_user)

