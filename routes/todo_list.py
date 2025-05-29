from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from db.database import get_session
from models.todo_list import Todo_List, Todo_ListCreate
from crud.todo_list import (
    create_todo_list,
    get_todo_lists,
    get_todo_list_by_id,
    get_todo_list_by_name,
    update_todo_list,
    delete_todo_list
)
from auth.dependencies import require_role

router = APIRouter()

@router.post("/", response_model = Todo_List)
def create(todo_list: Todo_ListCreate, session: Session = Depends(get_session), current_todo_list: dict = Depends(require_role("admin"))):
    try:
        todo_list_data = Todo_List(**todo_list.model_dump())
        return create_todo_list(session, todo_list_data)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/", response_model = list[Todo_List])
def read_all(session: Session = Depends(get_session), current_todo_list: dict = Depends(require_role("admin"))):
    try:
        return get_todo_lists(session)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/{todo_list_id}", response_model = Todo_List)
def read(todo_list_id: int, session: Session = Depends(get_session), current_todo_list: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        todo_list = get_todo_list_by_id(session, todo_list_id)
        if not todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with ID {todo_list_id} not found.")
        # If not admin, can't see todo_lists if not an owner.
        if current_todo_list.get("role") != "admin" and current_todo_list.get("name") != todo_list.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return todo_list
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/name/{name}", response_model = Todo_List)
def read_by_name(name: str, session: Session = Depends(get_session), current_todo_list: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        todo_list = get_todo_list_by_name(session, name)
        if not todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with name '{name}' not found.")
        # If not admin, can't see todo_lists if not an owner.
        if current_todo_list.get("role") != "admin" and current_todo_list.get("name") != todo_list.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return todo_list
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.put("/{todo_list_id}", response_model = Todo_List)
def update(
    todo_list_id: int,
    todo_list_data: dict = Body(
        ...,
        examples={
            "example": {
                "summary": "Update todo_list example",
                "value": {
                    "title": "Updated todo_list name",
                    "description": "Updated todo_list description",
                    "owner_id": 0
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_todo_list: dict = Depends(require_role(["admin", "user", "viewer"])),
):
    try:
        todo_list = get_todo_list_by_id(session, todo_list_id)
        if not todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with ID {todo_list_id} not found.")
        # If not admin, can't change todo_lists if not an owner.
        if current_todo_list.get("role") != "admin" and current_todo_list.get("name") != todo_list.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        updated_todo_list = update_todo_list(session, todo_list_id, todo_list_data)
        if not updated_todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with ID {todo_list_id} not found.")
        return updated_todo_list
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.delete("/{todo_list_id}", response_model = Todo_List)
def delete(todo_list_id: int, session: Session = Depends(get_session), current_todo_list: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        todo_list = get_todo_list_by_id(session, todo_list_id)
        if not todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with ID {todo_list_id} not found.")
        # If not admin, can't see todo_lists if not an owner.
        if current_todo_list.get("role") != "admin" and current_todo_list.get("name") != todo_list.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        deleted_todo_list = delete_todo_list(session, todo_list_id)
        if not deleted_todo_list:
            raise HTTPException(status_code = 404, detail = f"Todo_List with ID {todo_list_id} not found.")
        return deleted_todo_list
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")