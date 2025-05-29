from sqlmodel import SQLModel, Field
from typing import Optional

class Task_StatusBase(SQLModel):
    name: str
    color: Optional[str]

class Task_Status(Task_StatusBase, table=True):
    id: Optional[int] = Field(default = None, primary_key = True)

class Task_StatusCreate(Task_StatusBase):
    pass  # Excluir los campos que no están en la clase base.