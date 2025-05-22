from sqlmodel import Session, select
from models.task import Task
import datetime

def create_task(session: Session, task: Task):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_tasks(session: Session):
    return session.exec(select(Task)).all()

def get_task_by_id(session: Session, task_id: int):
    return session.get(Task, task_id)

def get_tasks_by_title(session: Session, title: str):
    statement = select(Task).where(Task.title == title)
    return session.exec(statement).all()

def get_tasks_by_due_date(session: Session, due_date: datetime):
    statement = select(Task).where(Task.due_date == due_date)
    return session.exec(statement).all()

def get_tasks_by_completed(session: Session, completed: bool):
    statement = select(Task).where(Task.completed == completed)
    return session.exec(statement).all()

def update_task(session: Session, task_id: int, task_data: dict):
    task = session.get(Task, task_id)
    if not task:
        return None
    for key, value in task_data.items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task

def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
    return task