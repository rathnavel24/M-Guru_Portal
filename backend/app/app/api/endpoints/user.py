from fastapi import APIRouter, BackgroundTasks, Depends
from backend.app.app.schemas.user_schema import UserSignUp, UserLogin, Paymentmail
from sqlalchemy.orm import Session
from backend.app.app.crud.user_crud import SignUpDetails, LoginUser, Logout
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.user_crud import SignUpDetails, LoginUser, UserServices
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.utils import send_invoice_email

router = APIRouter(tags=["login"])


@router.post("/signup")
async def signup(
    user_data: UserSignUp,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),
):
    try:
        return SignUpDetails(db, user_data).user_signup()
    except Exception as e:
        raise e


@router.post("/login")
async def login(
    data: UserLogin, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):

    return LoginUser(db, data.email, data.password).login(background_tasks)


# this is for view all user
@router.post("/logout")
async def log_out(
    current_user=Depends(role_required([1, 2])), db: Session = Depends(get_db)
):
    return Logout(db).logout(current_user)


@router.post("/payment_email")  # send payment email to student
async def payment_mail(
    data: Paymentmail,
    bgtask: BackgroundTasks,
    current_user=Depends(role_required([1])),
    db: Session = Depends(get_db),
):
    try:
        bgtask.add_task(send_invoice_email, data, db)
        return {"message": "Payment mail sent succesfully"}
    except Exception as e:
        raise e


# this is for view all user


@router.get("/get_userby_batch/{batch_id}")
async def get_userby_batch(
    batch_id, db: Session = Depends(get_db), current_user=Depends(role_required([1]))
):
    return UserServices(db, None).get_usersby_batch(batch_id)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),  # only admin
):
    return UserServices(db, None).soft_delete_user(user_id)
