import random
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI()
bearer = HTTPBearer()

SECRET_KEY = "super-secret-key-change-in-prod"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


class LoginRequest(BaseModel):
    username: str
    password: str


def authenticate_user(username: str, password: str) -> bool:
    return random.choice([True, False])


def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.post("/login")
def login(body: LoginRequest):
    if not authenticate_user(body.username, body.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_token(body.username)}


@app.get("/protected_resource")
def protected(username: str = Depends(verify_token)):
    return {"message": f"Access granted for {username}"}
