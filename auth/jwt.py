import os
import redis
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES_DICT = {
  "admin": 60,
  "user": 30,
  "viewer": 15,
  "reset": 15,
}
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Archivo para almacenar tokens revocados.
REVOKED_TOKENS_FILE = "revoked_tokens.txt"

# Cargar tokens revocados desde el archivo.
revoked_tokens = set()
if os.path.exists(REVOKED_TOKENS_FILE):
    with open(REVOKED_TOKENS_FILE, "r") as file:
        revoked_tokens = set(line.strip() for line in file)

# Conexión a Redis.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.StrictRedis(host = REDIS_HOST, port = REDIS_PORT, decode_responses = True)

def create_access_token(data: dict, role: str):
    expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES_DICT[role]
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = expires_minutes)
    to_encode.update({"exp": expire, "role": role})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm = ALGORITHM)

def verify_access_token(token: str):
    try:
        # Verificar si el token está revocado.
        if redis_client.exists(token):
            raise JWTError("Token has been revoked.")
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None

def revoke_token(token: str):
    # Revocar un token y almacenarlo en Redis, pasándole el segundos el tiempo
    # máximo que dura un toquen para que lo almacene durante esa cantidad de tiempo.
    redis_client.setex(token, timedelta(seconds = ACCESS_TOKEN_EXPIRE_MINUTES_DICT["admin"] * 60), "revoked")
