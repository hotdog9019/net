import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super-secret-key-change-in-prod"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

fake_users_db: dict[str, dict] = {}


class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.admin: ["create", "read", "update", "delete"],
    Role.user: ["read", "update"],
    Role.guest: ["read"],
}


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: Role = Role.guest


class LoginRequest(BaseModel):
    username: str
    password: str


def create_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "role": role, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_permission(permission: str):
    def checker(current_user: dict = Depends(get_current_user)):
        role = Role(current_user["role"])
        if permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return checker


@app.post("/register", status_code=201)
def register(body: RegisterRequest):
    for stored in fake_users_db:
        if secrets.compare_digest(stored, body.username):
            raise HTTPException(status_code=409, detail="User already exists")
    fake_users_db[body.username] = {
        "username": body.username,
        "hashed_password": pwd_context.hash(body.password),
        "role": body.role,
    }
    return {"message": f"User '{body.username}' registered with role '{body.role}'"}


@app.post("/login")
def login(body: LoginRequest):
    stored = None
    for stored_username, user_data in fake_users_db.items():
        if secrets.compare_digest(stored_username, body.username):
            stored = user_data
            break
    if stored is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(body.password, stored["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_token(stored["username"], stored["role"]), "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(current_user: dict = Depends(require_permission("read"))):
    return {"message": f"Welcome, {current_user['username']}! Role: {current_user['role']}"}


@app.post("/admin/resource")
def admin_create(current_user: dict = Depends(require_permission("create"))):
    return {"message": f"Resource created by admin '{current_user['username']}'"}


@app.put("/user/resource")
def user_update(current_user: dict = Depends(require_permission("update"))):
    return {"message": f"Resource updated by '{current_user['username']}'"}


@app.delete("/admin/resource")
def admin_delete(current_user: dict = Depends(require_permission("delete"))):
    return {"message": f"Resource deleted by admin '{current_user['username']}'"}
