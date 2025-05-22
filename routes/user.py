from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from db.database import get_session
from models.user import User, UserCreate
from crud.user import (
    create_user,
    get_users,
    get_user_by_id,
    get_user_by_name,
    update_user,
    update_user_by_name,
    delete_user,
    delete_user_by_name,
)
from auth.dependencies import get_current_user, require_role  # Import role-based dependency

router = APIRouter()

@router.post("/", response_model=User)
def create(author: UserCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        author_data = User(**author.model_dump())
        return create_user(session, author_data)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/", response_model=list[User])
def read_all(session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        return get_users(session)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/{user_id}", response_model=User)
def read(user_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        user = get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with ID {user_id} not found.")
        # If not admin, can't see users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.get("/name/{name}", response_model=User)
def read_by_name(name: str, session: Session = Depends(get_session), current_user: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        user = get_user_by_name(session, name)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with name '{name}' not found.")
        # If not admin, can't see users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        return user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.put("/{user_id}", response_model=User)
def update(
    user_id: int,
    user_data: dict = Body(
        ...,
        examples={
            "example": {
                "summary": "Update user example",
                "value": {
                    "name": "Updated user name",
                    "email": "updated_email@example.com"
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role(["admin", "user", "viewer"])),
):
    try:
        user = get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with ID {user_id} not found.")
        # If not admin, can't change users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        updated_user = update_user(session, user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code = 404, detail = f"User with ID {user_id} not found.")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.put("/name/{name}", response_model=User)
def update_by_name(
    name: str,
    user_data: dict = Body(
        ...,
        examples={
            "example": {
                "summary": "Update user example.",
                "value": {
                    "name": "Updated user name.",
                    "email": "updated_email@example.com"
                }
            }
        }
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role(["admin", "user", "viewer"])),
):
    try:
        user = get_user_by_name(session, name)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with name {name} not found.")
        # If not admin, can't change users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        updated_user = update_user_by_name(session, name, user_data)
        if not updated_user:
            raise HTTPException(status_code = 404, detail = f"User with name '{name}' not found.")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.delete("/{user_id}", response_model=User)
def delete(user_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role(["admin", "user", "viewer"]))):
    try:
        user = get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with ID {user_id} not found.")
        # If not admin, can't see users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        deleted_user = delete_user(session, user_id)
        if not deleted_user:
            raise HTTPException(status_code = 404, detail = f"User with ID {user_id} not found.")
        return deleted_user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")

@router.delete("/name/{name}", response_model=User)
def delete_by_name(name: str, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        user = get_user_by_name(session, name)
        if not user:
            raise HTTPException(status_code = 404, detail = f"User with name {name} not found.")
        # If not admin, can't see users other than oneself.
        if current_user.get("role") != "admin" and current_user.get("name") != user.name:
            raise HTTPException(status_code = 403, detail = "Insufficient permissions.")
        deleted_user = delete_user_by_name(session, name)
        if not deleted_user:
            raise HTTPException(status_code = 404, detail = f"User with name '{name}' not found.")
        return deleted_user
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Unexpected error: {str(e)}")
