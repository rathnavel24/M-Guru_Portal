from fastapi import HTTPException
from backend.app.app.models.portal_users import Users
from backend.app.app.models.tasks import Task
from backend.app.app.models.time_log import TimeLog
from backend.app.app.models.pass_log import PassLog
from sqlalchemy.orm import Session
from datetime import datetime
from abc import ABC, abstractmethod
from backend.app.app.schemas.task_schema import createTask, editTaskDetails, updateTask
from fastapi import status

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

    def _format_duration(self, total_seconds: int):
        hours = round(total_seconds / 3600, 2)
        minutes = round(total_seconds / 60, 2)
        return {
            "seconds": total_seconds,
            "minutes": minutes,
            "hours": hours,
        }

    def _get_task_or_404(self, task_id: int):
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="task not found")
        return task

    def _ensure_task_actor_allowed(self, task: Task, current_user: dict):
        current_user_id = current_user.get("user_id")
        current_user_role = current_user.get("role")

        if task.user_id == current_user_id or current_user_role in [1, 2]:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this task",
        )

    def _is_admin_or_mentor(self, current_user: dict):
        return current_user.get("role") in [1, 2]

    def _is_self_created_task(self, task: Task, current_user: dict):
        current_user_id = current_user.get("user_id")
        return (
            str(task.user_id) == str(current_user_id)
            and str(task.created_by) == str(current_user_id)
        )

    def _ensure_self_created_task_owner(self, task: Task, current_user: dict, action: str):
        if self._is_self_created_task(task, current_user):
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not allowed to {action} this task",
        )

    def _ensure_admin_task_edit_allowed(self, task: Task, current_user: dict):
        if not self._is_admin_or_mentor(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to edit this task",
            )
        return

    def _apply_task_updates(self, task: Task, update_data: dict):
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)

        return {"message": "task updated successfully", "task": self._serialize_task(task)}

    def _get_active_time_log(self, task_id: int, user_id: int):
        return (
            self.db.query(TimeLog)
            .filter(
                TimeLog.task_id == task_id,
                TimeLog.user_id == user_id,
                TimeLog.end_time.is_(None),
            )
            .order_by(TimeLog.start_time.desc())
            .first()
        )

    def _get_active_pass_log(self, task_id: int, user_id: int):
        return (
            self.db.query(PassLog)
            .filter(
                PassLog.task_id == task_id,
                PassLog.user_id == user_id,
                PassLog.resume_time.is_(None),
            )
            .order_by(PassLog.pass_time.desc())
            .first()
        )

    def _calculate_task_metrics(self, task_id: int, user_id: int):
        current_time = datetime.utcnow()
        productive_seconds = 0
        break_seconds = 0

        time_logs = (
            self.db.query(TimeLog)
            .filter(TimeLog.task_id == task_id, TimeLog.user_id == user_id)
            .all()
        )
        for log in time_logs:
            if log.start_time:
                end_time = log.end_time or current_time
                productive_seconds += max(
                    int((end_time - log.start_time).total_seconds()),
                    0,
                )

        pass_logs = (
            self.db.query(PassLog)
            .filter(PassLog.task_id == task_id, PassLog.user_id == user_id)
            .all()
        )
        for log in pass_logs:
            if log.pass_time:
                resume_time = log.resume_time or current_time
                break_seconds += max(
                    int((resume_time - log.pass_time).total_seconds()),
                    0,
                )

        return {
            "productive_time": self._format_duration(productive_seconds),
            "break_time": self._format_duration(break_seconds),
        }

    def _serialize_task(self, task: Task):
        current_time = datetime.utcnow()
        is_overdue = bool(task.due_time and task.due_time < current_time and task.status != 3)
        is_editable = str(task.created_by) == str(task.user_id)
        metrics = self._calculate_task_metrics(task.task_id, task.user_id)

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
            "productive_time": metrics["productive_time"],
            "break_time": metrics["break_time"],
        }

    def createTask(self, data: createTask, current_user: dict):
        user = self.db.query(Users).filter(Users.user_id == data.user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="user not found")

        if (
            not self._is_admin_or_mentor(current_user)
            and str(data.user_id) != str(current_user.get("user_id"))
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create tasks for yourself",
            )

        creator = data.created_by or str(current_user.get("user_id"))
        if not self._is_admin_or_mentor(current_user):
            creator = str(current_user.get("user_id"))

        new_task = Task(
            user_id=data.user_id,
            title=data.title,
            status=data.status,
            created_by=creator,
            due_time=data.due_time,
            description = data.description,
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
        task = self._get_task_or_404(task_id)
        is_admin_or_mentor = self._is_admin_or_mentor(current_user)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        if is_admin_or_mentor:
            disallowed_fields = set(update_data) - {"title", "due_time"}
            if disallowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin can only edit task title and due date",
                )
            self._ensure_admin_task_edit_allowed(task, current_user)
        else:
            self._ensure_self_created_task_owner(task, current_user, "edit")

        return self._apply_task_updates(task, update_data)

    def edit_task_details(self, task_id: int, data: editTaskDetails, current_user: dict):
        task = self._get_task_or_404(task_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        if self._is_admin_or_mentor(current_user):
            self._ensure_admin_task_edit_allowed(task, current_user)
        else:
            self._ensure_self_created_task_owner(task, current_user, "edit")

        return self._apply_task_updates(task, update_data)

    def change_task_status(self, task_id: int, status: int, current_user: dict):
        task = self._get_task_or_404(task_id)
        self._ensure_self_created_task_owner(task, current_user, "change the status of")
        task.status = status
        task.updated_at = datetime.utcnow()
        self.db.commit()
        return {"message": "task status updated successfully"}
    

    def start_task(self, task_id: int, current_user: dict):
        task = self._get_task_or_404(task_id)
        self._ensure_self_created_task_owner(task, current_user, "start")

        # Prevent restarting completed task
        if task.status == 3:
            raise HTTPException(
                status_code=400,
                detail="Completed task cannot be started again"
            )

        user_id = task.user_id

        if self._get_active_time_log(task_id, user_id):
            raise HTTPException(status_code=400, detail="Task already started")

        if self._get_active_pass_log(task_id, user_id):
            raise HTTPException(status_code=400, detail="Task is paused. Resume it instead")

        current_time = datetime.utcnow()

        if task.start_time is None:
            task.start_time = current_time

        task.status = 2
        task.updated_at = current_time

        new_log = TimeLog(
            task_id=task.task_id,
            user_id=user_id,
            start_time=current_time,
            status=1,
            productive=True,
            created_by=str(current_user.get("user_id")),
            updated_at=current_time,
        )

        self.db.add(new_log)
        self.db.commit()
        self.db.refresh(task)

        return {
            "message": "Task started successfully",
            "task": self._serialize_task(task),
        }

    def pause_task(self, task_id: int, reason: str, current_user: dict):
        task = self._get_task_or_404(task_id)
        self._ensure_self_created_task_owner(task, current_user, "pause")
        user_id = task.user_id
        log = self._get_active_time_log(task_id, user_id)

        if not log:
            raise HTTPException(status_code=404, detail="No active running task found")

        current_time = datetime.utcnow()
        log.end_time = current_time
        session_time = int((log.end_time - log.start_time).total_seconds())
        log.total_time = session_time
        log.productive = True
        log.status = 2
        log.updated_at = current_time

        pass_log = PassLog(
            task_id=task_id,
            user_id=user_id,
            pass_time=current_time,
            reason=reason,
            status="paused",
            created_by=str(current_user.get("user_id")),
            updated_at=current_time,
        )

        task.status = 4
        task.updated_at = current_time

        self.db.add(pass_log)
        self.db.commit()

        return {
            "message": "Task paused successfully",
            "session_time": self._format_duration(session_time),
            "task": self._serialize_task(task),
        }
    
    def resume_task(self, task_id: int, current_user: dict):
        task = self._get_task_or_404(task_id)
        self._ensure_self_created_task_owner(task, current_user, "resume")
        user_id = task.user_id
        pass_log = self._get_active_pass_log(task_id, user_id)

        if not pass_log:
            raise HTTPException(status_code=404, detail="No paused session found")

        current_time = datetime.utcnow()
        pass_log.resume_time = current_time
        pass_log.status = "resumed"
        pass_log.updated_at = current_time

        new_log = TimeLog(
            task_id=task_id,
            user_id=user_id,
            start_time=current_time,
            status=1,
            productive=True,
            created_by=str(current_user.get("user_id")),
            updated_at=current_time,
        )

        task.status = 2
        task.updated_at = current_time

        self.db.add(new_log)
        self.db.commit()

        return {
            "message": "Task resumed successfully",
            "task": self._serialize_task(task),
        }

    def stop_task(self, task_id: int, current_user: dict):
        task = self._get_task_or_404(task_id)
        self._ensure_self_created_task_owner(task, current_user, "stop")
        user_id = task.user_id
        current_time = datetime.utcnow()

        active_log = self._get_active_time_log(task_id, user_id)
        if active_log:
            active_log.end_time = current_time
            active_log.total_time = int(
                (active_log.end_time - active_log.start_time).total_seconds()
            )
            active_log.productive = True
            active_log.status = 3
            active_log.updated_at = current_time

        active_pass_log = self._get_active_pass_log(task_id, user_id)
        if active_pass_log:
            active_pass_log.resume_time = current_time
            active_pass_log.status = "stopped"
            active_pass_log.updated_at = current_time

        task.status = 3
        task.completion_time = current_time
        if task.start_time is None:
            task.start_time = current_time
        task.updated_at = current_time

        self.db.commit()
        self.db.refresh(task)
        return {
            "message": "Task stopped successfully",
            "task": self._serialize_task(task),
        }

    def delete_task(self, task_id: int, current_user: dict):
        task = self._get_task_or_404(task_id)

        if self._is_admin_or_mentor(current_user):
            self.db.query(PassLog).filter(PassLog.task_id == task_id).delete()
            self.db.query(TimeLog).filter(TimeLog.task_id == task_id).delete()
            self.db.delete(task)
            self.db.commit()
            return {"message": "task deleted successfully"}

        self._ensure_self_created_task_owner(task, current_user, "delete")

        self.db.query(PassLog).filter(PassLog.task_id == task_id).delete()
        self.db.query(TimeLog).filter(TimeLog.task_id == task_id).delete()
        self.db.delete(task)
        self.db.commit()
        return {"message": "task deleted successfully"}
