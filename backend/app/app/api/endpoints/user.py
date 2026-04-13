from fastapi import APIRouter, BackgroundTasks, Depends
from backend.app.app.schemas.user_schema import (
    AdminResetPassword,
    ChangePassword,
    UserSignUp,
    UserLogin,
    Paymentmail,
    UserUpdate,
)
from sqlalchemy.orm import Session
from backend.app.app.crud.user_crud import SignUpDetails, LoginUser, Logout, GetEmail
from backend.app.app.crud.user_crud import SignUpDetails, LoginUser, Logout
from backend.app.app.api.deps import get_current_user, get_db, role_required
from backend.app.app.crud.user_crud import SignUpDetails, LoginUser, UserServices
from backend.app.app.crud.dashboard import dashboard
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.email_services import send_invoice_email, get_bankdetail,payment_confirmation_service
from fastapi import Query

router = APIRouter(tags=["login"])


@router.post("/signup")
async def signup(
    user_data: UserSignUp,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),):
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
    current_user=Depends(role_required([1, 2, 4])), db: Session = Depends(get_db)
):
    return Logout(db).logout(current_user)


@router.post("/payment_email")  # send payment email to student
async def payment_mail(
    data: Paymentmail,
    current_user=Depends(role_required([1])),
    db: Session = Depends(get_db),
):
    try:
        await send_invoice_email(data, current_user, db)
        return {"message": "email sent to the user"}
    except Exception as e:
        raise e
    
@router.post("/payment_confirmation")
async def payment_confirmation_api(
    invoice_no: str,
    current_user=Depends(role_required([1])),
    db: Session = Depends(get_db)
):
    try:
        return payment_confirmation_service(invoice_no, db)
    except Exception as e:
        raise e
    
# @router.get("/test_reminder")
# async def test_reminder():
#     from backend.app.app.crud.auto_remainder import send_auto_reminders
#     await send_auto_reminders()   # CORRECT
#     return {"message": "Reminder executed"}


@router.post("/dashboard")
async def get_dashboard(
    batch_id: int = None,
    current_user=Depends(role_required([1])),  # only admin
    db: Session = Depends(get_db),
):
    return dashboard(batch_id, db)


@router.post("/get_bankdetails")
async def get_bankdetails(
    invoice_no: str,
    current_user=Depends(role_required([1])),
    db: Session = Depends(get_db),
):
    try:
        return get_bankdetail(invoice_no, db)
    except:
        return " Invalid error "

# this is for view all user
@router.get("/get_userby_batch/{batch_id}")
async def get_userby_batch(
    batch_id,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,4])), 
):
    return UserServices(db, None).get_usersby_batch(batch_id)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),  # only admin
):
    return UserServices(db, None).soft_delete_user(user_id)


@router.get("/emails")
async def get_emails(
    page_no: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),
):
    return GetEmail(db).get_all_emails(page_no, page_size)


@router.get("/emails/{batch_id}")
async def get_emails(
    batch_id: int,
    page_no: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),
):
    return GetEmail(db).get_all_emails_bybatch(batch_id, page_no, page_size)


@router.get("/batches")
async def get_batches(
    db: Session = Depends(get_db), current_user=Depends(role_required([1,4]))
):
    return UserServices(db, None).get_all_batches()


@router.get("/get_all_users")
async def get_all_users(
    page_no: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,4])),
):
    return UserServices(db, None).get_all_users(page_no, page_size)


@router.get("/me")
def get_user(
    db: Session = Depends(get_db), current_user=Depends(role_required([1, 2, 4]))
):
    return UserServices(db, None).get_user(current_user.get("user_id"))


@router.put("/update_users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1])),  # optional admin only
):
    return UserServices(db, None).update_user(user_id, data)

@router.post("/exam/logout")
def exam_logout(user_id: int, db: Session = Depends(get_db)):
    return Logout(db).logout_exam_user(user_id)

@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 2, 4]))  # all users
):
    return UserServices(db, None).change_password(current_user, data)

@router.post("/admin/reset-password")
def admin_reset_password(
    data: AdminResetPassword,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1]))  # admin only
):
    return UserServices(db, None).admin_reset_password(data)