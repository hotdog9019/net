import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, dict] = {}


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    username_match = secrets.compare_digest(credentials.username, user["username"])
    password_ok = pwd_context.verify(credentials.password, user["hashed_password"])
    if not (username_match and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return UserInDB(username=user["username"], hashed_password=user["hashed_password"])


@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed,
    }
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(current_user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {current_user.username}!"}
