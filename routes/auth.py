from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from auth.jwt import create_access_token, create_refresh_token, verify_refresh_token, revoke_token, verify_access_token
from auth.hashing import hash_password, verify_password
from db.database import get_session
from auth.dependencies import get_current_user, oauth2_scheme
from models.user import User, UserCreate, UserRead

router = APIRouter()
templates = Jinja2Templates(directory = "templates")

@router.post("/register", response_model = UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code = 400, detail = "Name already exists.")
    if user.role != "viewer" and user.role != "user":
        raise HTTPException(status_code = 400, detail = "Invalid role.")
    hashed_password = hash_password(user.password)
    new_user = User(
        name = user.name,
        email = user.email,
        hashed_password = hashed_password,
        role = user.role
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.name == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code = 401, detail = "Invalid credentials.")
    token = create_access_token({"name": user.name}, role = user.role)
    refresh_token = create_refresh_token({"name": user.name})
    user.refresh_token = refresh_token
    session.add(user)
    session.commit()
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str, session: Session = Depends(get_session)):
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code = 401, detail = "Invalid or expired refresh token.")
    user = session.query(User).filter(User.refresh_token == refresh_token).first()
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    new_access_token = create_access_token({"name": user.name}, role=user.role)
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.name == current_user["name"]).first()
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found.")
    user.refresh_token = None
    session.add(user)
    session.commit()

    # Revocar el token de acceso.
    revoke_token(token)

    return {"message": "Successfully logged out."}

@router.get("/forgot-password", response_class = HTMLResponse)
def forgot_password_view(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
def forgot_password(email: str = Form(...), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found.")
    
    # Generar token de recuperación.
    token = create_access_token({"name": user.email}, role = "reset")
    
    # Devolver el token directamente.
    return {"message": "Use this token to reset your password.", "token": token}

@router.post("/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), session: Session = Depends(get_session)):
    payload = verify_access_token(token)
    print(payload)
    if not payload or payload.get("role") != "reset":
        raise HTTPException(status_code = 401, detail = "Invalid or expired token.")
    
    user = session.query(User).filter(User.email == payload["name"]).first()
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found.")
    
    # Actualizar contraseña.
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()

    return {"message": "Password successfully reset."}
