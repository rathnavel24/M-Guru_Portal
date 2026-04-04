from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.task_crud import Tasks
from backend.app.app.schemas.task_schema import createTask
router = APIRouter(prefix="/task", tags=["Task"])


@router.post("/create")
def create_task(data: createTask, db: Session = Depends(get_db),
                        current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.createTask(data)
@router.get("/user_tasks")
def get_user_tasks(db: Session = Depends(get_db),
                        current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.get_user_task(current_user.get("user_id"))

@router.put("/{task_id}/status/{status}")
def change_task_status(task_id: int, status: int, 
                       db: Session = Depends(get_db),
                        current_user=Depends(role_required([1,2,3,4]))):

    service = Tasks(db)
    return service.change_task_status(task_id, status)