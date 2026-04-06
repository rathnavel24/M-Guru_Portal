from fastapi import HTTPException
from backend.app.app.models.portal_users import Users
from backend.app.app.models.tasks import Task
from backend.app.app.models.time_log import TimeLog
from backend.app.app.models.pass_log import PassLog
from sqlalchemy.orm import Session
from datetime import datetime
from abc import ABC, abstractmethod
from backend.app.app.schemas.task_schema import createTask, updateTask
from fastapi import status
from datetime import datetime

class AbstractTask(ABC):

    @abstractmethod
    def createTask():
        pass
'''
    @abstractmethod
    def get_user_task():
        pass
    @abstractmethod
    def completed_task():
        pass
    @abstractmethod
    def pending_task():
        pass
    @abstractmethod
    def overdue_task():
        pass
'''


class Tasks(AbstractTask):

    def __init__(self, db: Session):
        self.db = db

    def _serialize_task(self, task: Task):
        current_time = datetime.utcnow()
        is_overdue = bool(task.due_time and task.due_time < current_time and task.status != 3)
        is_editable = str(task.created_by) == str(task.user_id)

        return {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "title": task.title,
            "status": task.status,
            "start_time": task.start_time,
            "completion_time": task.completion_time,
            "created_at": task.created_at,
            "created_by": task.created_by,
            "updated_at": task.updated_at,
            "due_time": task.due_time,
            "is_editable": is_editable,
            "is_overdue": is_overdue,
        }

    def createTask(self, data: createTask, current_user: dict):
        user = self.db.query(Users).filter(Users.user_id == data.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="user not found")

        creator = data.created_by or str(current_user.get("user_id"))

        new_task = Task(
            user_id=data.user_id,
            title=data.title,
            status=data.status,
            created_by=creator,
            due_time=data.due_time,
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return {"message": "task created successfully", "task": self._serialize_task(new_task)}

    def get_user_task(self, user_id: int):
        current_time = datetime.utcnow()
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                (Task.due_time.is_(None)) | (Task.due_time >= current_time),
            )
            .order_by(Task.created_at.desc())
            .all()
        )
        return [self._serialize_task(task) for task in tasks]

    def get_overdue_tasks(self, user_id: int):
        current_time = datetime.utcnow()
        tasks = (
            self.db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.due_time.is_not(None),
                Task.due_time < current_time,
                Task.status != 3,
            )
            .order_by(Task.due_time.asc())
            .all()
        )
        return [self._serialize_task(task) for task in tasks]

    def update_task(self, task_id: int, data: updateTask, current_user: dict):
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="task not found")

        current_user_id = current_user.get("user_id")
        current_user_role = current_user.get("role")
        is_admin_or_mentor = current_user_role in [1, 2]
        is_self_created_task = (
            task.user_id == current_user_id and str(task.created_by) == str(current_user_id)
        )

        if not (is_admin_or_mentor or is_self_created_task):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to edit this task",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return {"message": "task updated successfully", "task": self._serialize_task(task)}

    def change_task_status(self, task_id: int, status: int):
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="task not found")
        task.status = status
        task.updated_at = datetime.utcnow()
        self.db.commit()
        return {"message": "task status updated successfully"}
    

    def start_task(self, task_id: int, current_user: dict):
        task = self.db.query(Task).filter(Task.task_id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Optional: prevent restarting
        if task.status == 2:  # already in progress
            raise HTTPException(status_code=400, detail="Task already started")

        current_time = datetime.utcnow()

        # Update task
        task.status = 2  # in_progress
        task.start_time = current_time
        task.updated_at = current_time

        # Create timelog
        new_log = TimeLog(
            task_id=task.task_id,
            user_id=current_user.get("user_id"),
            start_time=current_time,
            # end_time = None (automatically)
            status=1,
            created_by=str(current_user.get("user_id"))
        )

        self.db.add(new_log)
        self.db.commit()

        return {"message": "Task started successfully"}

    def pause_task(self, task_id: int, reason: str, current_user: dict):
        user_id = current_user.get("user_id")

        # Get active timelog
        log = self.db.query(TimeLog).filter(
            TimeLog.task_id == task_id,
            TimeLog.user_id == user_id,
            TimeLog.end_time.is_(None)
        ).first()

        if not log:
            raise HTTPException(status_code=404, detail="No active running task found")

        current_time = datetime.utcnow()

        # End current session
        log.end_time = current_time

        session_time = int((log.end_time - log.start_time).total_seconds())

        # accumulate time (important if reused)
        log.total_time = (log.total_time or 0) + session_time

        # Create pass log
        pass_log = PassLog(
            task_id=task_id,
            user_id=user_id,
            pass_time=current_time,
            reason=reason,
            status="paused",
            created_by=str(user_id)
        )

        # Update task status
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        task.status = 4  # paused (define this in your enum logic)
        task.updated_at = current_time

        self.db.add(pass_log)
        self.db.commit()

        return {
            "message": "Task paused successfully",
            "session_time": session_time
        }
    
    def resume_task(self, task_id: int, current_user: dict):
        user_id = current_user.get("user_id")

        # Get last pause entry
        pass_log = self.db.query(PassLog).filter(
            PassLog.task_id == task_id,
            PassLog.user_id == user_id,
            PassLog.resume_time.is_(None)
        ).order_by(PassLog.pass_time.desc()).first()

        if not pass_log:
            raise HTTPException(status_code=404, detail="No paused session found")

        current_time = datetime.utcnow()

        # update resume time
        pass_log.resume_time = current_time

        #create new timelog session
        new_log = TimeLog(
            task_id=task_id,
            user_id=user_id,
            start_time=current_time,
            status=1,
            created_by=str(user_id)
        )

        # update task
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        task.status = 2  # in_progress
        task.updated_at = current_time

        self.db.add(new_log)
        self.db.commit()

        return {"message": "Task resumed successfully"}