from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from routes import user, todo_list, task, task_status, auth
from seeder import seed_data_if_missing
import uvicorn

# Load environment variables from .env file.
load_dotenv()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/auth/login")

# Configuración de Jinja2.
templates = Jinja2Templates(directory = "templates")

# Definir las rutas de la API.
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(todo_list.router, prefix="/api/todo_list", tags=["Todo list"])
app.include_router(task.router, prefix="/api/task", tags=["Task"])
app.include_router(task_status.router, prefix="/api/task_status", tags=["Task status"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Manejo de excepciones globales.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "error": str(exc)},
    )

# Se asegura de que la base de datos tenga información.
seed_data_if_missing()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
