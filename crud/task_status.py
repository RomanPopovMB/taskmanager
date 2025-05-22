from sqlmodel import Session, select
from models.task_status import Task_Status
import datetime

def create_task_status(session: Session, task_status: Task_Status):
    session.add(task_status)
    session.commit()
    session.refresh(task_status)
    return task_status

def get_task_statuses(session: Session):
    return session.exec(select(Task_Status)).all()

def get_task_status_by_id(session: Session, task_status_id: int):
    return session.get(Task_Status, task_status_id)

def update_task_status(session: Session, task_status_id: int, task_status_data: dict):
    task_status = session.get(Task_Status, task_status_id)
    if not task_status:
        return None
    for key, value in task_status_data.items():
        setattr(task_status, key, value)
    session.commit()
    session.refresh(task_status)
    return task_status

def delete_task_status(session: Session, task_status_id: int):
    task_status = session.get(Task_Status, task_status_id)
    if task_status:
        session.delete(task_status)
        session.commit()
    return task_status