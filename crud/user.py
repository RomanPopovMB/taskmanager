from sqlmodel import Session, select
from models.user import User

def create_user(session: Session, user: User):
    # Unique name check.
    existing_user = session.exec(select(User).where(User.name == user.name)).first()
    if existing_user:
        raise ValueError(f"An user with name '{user.name}' already exists.")
    # Unique email check.
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise ValueError(f"An user with email '{user.email}' already exists.")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_users(session: Session):
    return session.exec(select(User)).all()

def get_user_by_id(session: Session, user_id: int):
    return session.get(User, user_id)

def get_user_by_name(session: Session, name: str):
    statement = select(User).where(User.name == name)
    return session.exec(statement).first()

def update_user(session: Session, user_id: int, user_data: dict):
    user = session.get(User, user_id)
    if not user:
        return None
    for key, value in user_data.items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user

def update_user_by_name(session: Session, name: str, user_data: dict):
    statement = select(User).where(User.name == name)
    user = session.exec(statement).first()
    if not user:
        return None
    for key, value in user_data.items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
    return user

def delete_user_by_name(session: Session, name: str):
    statement = select(User).where(User.name == name)
    user = session.exec(statement).first()
    if user:
        session.delete(user)
        session.commit()
    return user