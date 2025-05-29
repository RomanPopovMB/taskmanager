from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from db.database import get_session
from models.task import Task, TaskCreate
from crud.task import (
    create_task,
    get_tasks,
    get_task_by_id,
    get_tasks_by_title,
    get_tasks_by_due_date,
    update_task,
    delete_task
)
from auth.dependencies import require_role, get_current_user
from crud.todo_list import (
    get_todo_list_by_id
)
from crud.user import (
    get_user_by_id
)
import datetime

router = APIRouter()

@router.post("/", response_model = Task)
def create(task: TaskCreate, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin"]))):
    try:
        task_data = Task(**task.model_dump())
        return create_task(session, task_data)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/", response_model = list[Task])
def read_all(session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin"]))):
    try:
        return get_tasks(session)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/{task_id}", response_model = Task)
def read(task_id: int, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        task = get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
        # If not admin, can't see tasks if not an owner.
        todo_list = get_todo_list_by_id(task.get("todo_list_id"))
        if not todo_list:
            raise HTTPException(status_code = 403, detail = "No todo list found for that task.")
        current_user = get_current_user()
        if current_user.get("role") != "admin":
            user = get_user_by_id(todo_list.owner_id)
            if not user:
                raise HTTPException(status_code = 403, detail = "Error finding user corresponding to the task's todo list.")
            if user.id != current_user.id:
                raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/title/{title}", response_model = Task)
def read_by_name(title: str, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        task = get_tasks_by_title(session, title)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task with title '{title}' not found.")
        # If not admin, can't see tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("title") != task.title:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")
        return task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/due_date/{due_date}", response_model = Task)
def read_by_due_date(due_date: datetime.date, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        task = get_tasks_by_due_date(session, due_date)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task with due date '{due_date}' not found.")
        # If not admin, can't see tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("due_date") != task.due_date:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/completed/{completed}", response_model = Task)
def read_by_completed(completed: bool, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        task = get_tasks_by_due_date(session, completed)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task with completed status '{completed}' not found.")
        # If not admin, can't see tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("completed") != task.completed:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.put("/{task_id}", response_model = Task)
def update(
    task_id: int,
    task_data: dict = Body(
        ...,
        examples={
            "example": {
                "summary": "Update task example",
                "value": {
                    "title": "Updated task title",
                    "description": "Updated task description",
                    "due_date": "2025-01-01 00:00:00.000000",
                    "completed": False,
                    "status_id": 1
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_task: dict = Depends(require_role(["admin", "user", "viewer"])),
):
    try:
        task = get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task with ID {task_id} not found.")
        # If not admin, can't change tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("name") != task.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        updated_task = update_task(session, task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code = 404, detail = f"Task with ID {task_id} not found.")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.delete("/{task_id}", response_model = Task)
def delete(task_id: int, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        task = get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task with ID {task_id} not found.")
        # If not admin, can't see tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("name") != task.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        deleted_task = delete_task(session, task_id)
        if not deleted_task:
            raise HTTPException(status_code = 404, detail = f"Task with ID {task_id} not found.")
        return deleted_task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")