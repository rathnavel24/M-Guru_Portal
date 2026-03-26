from fastapi import APIRouter, BackgroundTasks,Depends
from backend.app.app.schemas.user_schema import UserSignUp,UserLogin
from sqlalchemy.orm import Session
from backend.app.app.crud.user_crud import SignUpDetails,LoginUser,UserServices
from backend.app.app.api.deps import get_db
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

@router.get("/get_userby_batch/{batch_id}")
async def get_userby_batch(batch_id,db: Session = Depends(get_db)):
     return UserServices(db,None).get_usersby_batch(batch_id)
