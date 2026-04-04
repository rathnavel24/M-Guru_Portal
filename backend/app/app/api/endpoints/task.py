from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.task_crud import Tasks
from backend.app.app.schemas.task_schema import createTask
router = APIRouter(prefix="/task", tags=["Task"])


@router.post("/create")
def create_task(data: createTask, db: Session = Depends(get_db)):
    service = Tasks(db)
    return service.createTask(data)
@router.get("/user/{user_id}")
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    service = Tasks(db)
    return service.get_user_task(user_id)