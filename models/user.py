from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    name: str = Field(index = True, unique = True)
    email: EmailStr = Field(index = True, unique = True)  # EmailStr para validación de email.
    role: str = Field(default = "user")

class User(UserBase, table=True):
    id: Optional[int] = Field(default = None, primary_key = True)
    hashed_password: str
    refresh_token: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int