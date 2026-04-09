from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.task_crud import Tasks
from backend.app.app.schemas.pause_request import PauseRequest
from backend.app.app.schemas.task_schema import createTask, editTaskDetails, updateTask

router = APIRouter(prefix="/task", tags=["Task"])


@router.post("/create")
def create_task(data: createTask, db: Session = Depends(get_db),
                        current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.createTask(data, current_user)


@router.get("/user_tasks")
def get_user_tasks(db: Session = Depends(get_db),
                        current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.get_user_task(current_user.get("user_id"))


@router.get("/user_tasks/overdue")
def get_overdue_user_tasks(db: Session = Depends(get_db),
                           current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.get_overdue_tasks(current_user.get("user_id"))


@router.put("/edit/{task_id}")
def update_task(task_id: int, data: updateTask,
                db: Session = Depends(get_db),
                current_user=Depends(role_required([1,2,3,4]))):
    service = Tasks(db)
    return service.update_task(task_id, data, current_user)


# @router.patch("/{task_id}/details")
# def edit_task_details(task_id: int, data: editTaskDetails,
#                       db: Session = Depends(get_db),
#                       current_user=Depends(role_required([1,2,3,4]))):
#     service = Tasks(db)
#     return service.edit_task_details(task_id, data, current_user)


# @router.put("/{task_id}/status/{status}")
# def change_task_status(task_id: int, status: int, 
#                        db: Session = Depends(get_db),
#                         current_user=Depends(role_required([1,2,3,4]))):
#     service = Tasks(db)
#     return service.change_task_status(task_id, status, current_user)
@router.post("/{task_id}/start")
def start_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,2,3,4]))
):
    service = Tasks(db)
    return service.start_task(task_id, current_user)


@router.post("/{task_id}/pause")
def pause_task(
    task_id: int,
    payload: PauseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,2,3,4]))
):
    service = Tasks(db)
    return service.pause_task(task_id, payload.reason, current_user)
@router.post("/{task_id}/resume")
def resume_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,2,3,4]))
):
    service = Tasks(db)
    return service.resume_task(task_id, current_user)

@router.post("/{task_id}/stop")
def stop_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,2,3,4]))
):
    service = Tasks(db)
    return service.stop_task(task_id, current_user)
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1,2,3,4]))
):
    service = Tasks(db)
    return service.delete_task(task_id, current_user)
