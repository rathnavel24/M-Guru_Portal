from fastapi import APIRouter, BackgroundTasks,Depends
from backend.app.app.schemas.user_schema import UserSignUp,UserLogin,Paymentmail
from sqlalchemy.orm import Session
from backend.app.app.crud.user_crud import SignUpDetails,LoginUser,ViewUser
from backend.app.app.api.deps import get_db
from backend.app.app.utils import send_invoice_email
router = APIRouter(tags=["login"])

@router.post("/signup")
async def signup(user_data:UserSignUp,db:Session =  Depends(get_db)):
        try :
            return SignUpDetails(db,user_data).user_signup()
        except Exception as e:
             raise e

@router.post("/login")
async def login(data: UserLogin,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    return LoginUser(db, data.email, data.password).login(background_tasks)

@router.post("/payment_email") #send payment email to student
async def payment_mail(data:Paymentmail,bgtask:BackgroundTasks,db:Session = Depends(get_db)):
     try:
          bgtask.add_task(send_invoice_email,data,db)
          return {"message":"Payment mail sent succesfully"}
     except Exception as e:
          raise e

#this is for view all user 
@router.post("/view_user")
async def viewuser(batch:int ,db: Session = Depends(get_db)):
    return ViewUser(db).view_user(batch)


