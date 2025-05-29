from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from db.database import get_session
from models.task_status import Task_Status, Task_StatusCreate
from crud.task_status import (
    create_task_status,
    get_task_statuses,
    get_task_status_by_id,
    update_task_status,
    delete_task_status
)
from auth.dependencies import require_role, get_current_user
from crud.todo_list import (
    get_todo_list_by_id
)
from crud.user import (
    get_user_by_id
)

router = APIRouter()

@router.post("/", response_model = Task_Status)
def create(task: Task_StatusCreate, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin"]))):
    try:
        task_data = Task_Status(**task.model_dump())
        return create_task_status(session, task_data)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/", response_model = list[Task_Status])
def read_all(session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user"]))):
    try:
        return get_task_statuses(session)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/{task_id}", response_model = Task_Status)
def read(task_id: int, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin", "user"]))):
    try:
        task_status = get_task_status_by_id(session, task_id)
        if not task_status:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.put("/{task_id}", response_model = Task_Status)
def update(
    task_id: int,
    task_data: dict = Body(
        ...,
        examples={
            "example": {
                "summary": "Update task status example",
                "value": {
                    "name": "Updated task status name",
                    "description": "Updated task status color"
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_task: dict = Depends(require_role(["admin"])),
):
    try:
        task = get_task_status_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
        # If not admin, can't change tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("name") != task.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        updated_task = update_task_status(session, task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.delete("/{task_id}", response_model = Task_Status)
def delete(task_id: int, session: Session = Depends(get_session), current_task: dict = Depends(require_role(["admin"]))):
    try:
        task = get_task_status_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
        # If not admin, can't see tasks if not an owner.
        if current_task.get("role") != "admin" and current_task.get("name") != task.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        deleted_task = delete_task_status(session, task_id)
        if not deleted_task:
            raise HTTPException(status_code = 404, detail = f"Task status with ID {task_id} not found.")
        return deleted_task
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")