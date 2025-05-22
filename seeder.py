from sqlmodel import SQLModel, Session
from db.database import engine, create_db_and_tables, drop_db_and_tables, get_session
from models.user import User
from models.todo_list import Todo_List
from models.task import Task
from models.task_status import Task_Status
from crud.user import get_users
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from auth.hashing import hash_password

# Comprueba si puede hacer un get de los usuarios. Si falla,
# construye la base de datos.
def seed_data_if_missing():
    # Cargar las variables de environment.
    load_dotenv()
    session = get_session()
    try:
        return get_users(session)
    except Exception as e:
        seed_data()

def seed_data():
    # Cargar las variables de environment.
    load_dotenv()
    # Borrar la base de datos y las tablas existentes.
    drop_db_and_tables() 
    # Crear la base de datos y las tablas.
    create_db_and_tables()

    with Session(engine) as session:
        # Crear usuarios.
        try:
            user1 = User(name = "User", email = "alex.morgan@example.com", hashed_password = hash_password("123"), role = "user")
            user2 = User(name = "Admin", email = "sarah.jenkins@example.com", hashed_password = hash_password("123"), role = "admin")
            user3 = User(name = "Viewer", email = "michael.smith@example.com", hashed_password = hash_password("123"), role = "viewer")
            user4 = User(name = "Emily", email = "emily.davis@example.com", hashed_password = hash_password("123"), role = "user")
            user5 = User(name = "John", email = "john.taylor@example.com", hashed_password = hash_password("123"), role = "user")
            session.add_all([
                user1,
                user2,
                user3,
                user4,
                user5,
            ])
            session.commit()
        except Exception as e:
            print(f"Error creating users: {e}")

        # Crear todo lists.
        try:
            todo_list1 = Todo_List(title = "Grocery list", description = "Weekly", owner_id = user1.id)
            todo_list2 = Todo_List(title = "Work tasks", description = "", owner_id = user3.id)
            session.add_all([
                todo_list1,
                todo_list2,
            ])
            session.commit()
        except Exception as e:
            print(f"Error creating todo lists: {e}")

        # Crear task status.
        try:
            task_status1 = Task_Status(name = "In progress", color = "Yellow")
            task_status2 = Task_Status(name = "Done", color = "Green")
            session.add_all([
                task_status1,
                task_status2,
            ])
            session.commit()
        except Exception as e:
            print(f"Error creating task status: {e}")

        # Crear tasks.
        try:
            task1 = Task(title = "Eggs", description = "", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list1.id, status_id = task_status1.id)
            task2 = Task(title = "Milk", description = "", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list1.id, status_id = task_status1.id)
            task3 = Task(title = "Bread", description = "", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list1.id, status_id = task_status1.id)
            task4 = Task(title = "Tomatoes", description = "", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list1.id, status_id = task_status1.id)
            task5 = Task(title = "Email John", description = "About stuff.", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list2.id, status_id = task_status1.id)
            task6 = Task(title = "Finish reports", description = "", due_date = datetime.now(timezone.utc) + timedelta(days = 7), 
                         is_completed = False, todo_list_id = todo_list2.id, status_id = task_status1.id)
            task7 = Task(title = "Commit fraud", description = "Don't get caught.", due_date = datetime.now(timezone.utc) + timedelta(days = 14), 
                         is_completed = False, todo_list_id = todo_list2.id, status_id = task_status1.id)
            session.add_all([
                task1,
                task2,
                task3,
                task4,
                task5,
                task6,
                task7,
            ])
            session.commit()
        except Exception as e:
            print(f"Error creating tasks: {e}")

if __name__ == "__main__":
    seed_data()
