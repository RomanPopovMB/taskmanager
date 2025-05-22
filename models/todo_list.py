from sqlmodel import SQLModel, Field
from typing import Optional

class Todo_ListBase(SQLModel):
    title: str
    description: Optional[str]
    owner_id: int = Field(foreign_key = "user.id", ondelete = "CASCADE")

class Todo_List(Todo_ListBase, table=True):
    id: Optional[int] = Field(default = None, primary_key = True)

class Todo_ListCreate(Todo_ListBase):
    pass  # Excluir los campos que no están en la clase base.