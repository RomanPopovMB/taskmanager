from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta

class TaskBase(SQLModel):
    title: str
    description: Optional[str]
    due_date: datetime = Field(default_factory = lambda: datetime.now(timezone.utc) + timedelta(days = 7))
    is_completed: bool
    todo_list_id: int = Field(foreign_key = "todo_list.id", ondelete = "CASCADE")
    status_id: int = Field(foreign_key = "task_status.id", ondelete = "CASCADE")

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default = None, primary_key = True)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc))

class TaskCreate(TaskBase):
    pass  # Excluir los campos que no están en la clase base.