from fastapi import HTTPException
from backend.app.app.models.portal_users import Users
from backend.app.app.models.tasks import Task
from backend.app.app.models.time_log import TimeLog
from backend.app.app.models.pass_log import PassLog
from sqlalchemy.orm import Session
from datetime import datetime
from abc import ABC,abstractmethod
from backend.app.app.schemas.task_schema import createTask
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
    
    def  __init__(self,db : Session):
        self.db = db


    def createTask(self,data:createTask):
        
        user = self.db.query(Users).filter(Users.user_id == data.user_id).first()

        if not user :
            raise HTTPException(status_code = 404 , detail= "user not found" )
        
        new_task = Task(
            user_id = data.user_id,
            title = data.title,
            status = data.status,
            created_by = data.created_by,
            due_time = data.due_time
        )
        self.db.add(new_task)
        self.db.commit()
        return {"message" : "task created successfully"}
    
    def get_user_task(self,user_id:int):
        tasks = self.db.query(Task).filter(Task.user_id == user_id).all()
        return tasks
    def change_task_status(self,task_id:int,status:int):
        task = self.db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code = 404 , detail= "task not found" )
        task.status = status
        self.db.commit()
        return {"message" : "task status updated successfully"}