from sqlmodel import Session, select
from models.todo_list import Todo_List

def create_todo_list(session: Session, todo_list: Todo_List):
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    return todo_list

def get_todo_lists(session: Session):
    return session.exec(select(Todo_List)).all()

def get_todo_list_by_id(session: Session, todo_list_id: int):
    return session.get(Todo_List, todo_list_id)

def get_todo_list_by_name(session: Session, name: str):
    statement = select(Todo_List).where(Todo_List.name == name)
    return session.exec(statement).first()

def update_todo_list(session: Session, todo_list_id: int, todo_list_data: dict):
    todo_list = session.get(Todo_List, todo_list_id)
    if not todo_list:
        return None
    for key, value in todo_list_data.items():
        setattr(todo_list, key, value)
    session.commit()
    session.refresh(todo_list)
    return todo_list

def delete_todo_list(session: Session, todo_list_id: int):
    todo_list = session.get(Todo_List, todo_list_id)
    if todo_list:
        session.delete(todo_list)
        session.commit()
    return todo_list