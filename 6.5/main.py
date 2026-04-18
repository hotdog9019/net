import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "super-secret-key-change-in-prod"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

fake_users_db: dict[str, dict] = {}


class UserCredentials(BaseModel):
    username: str
    password: str


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


@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, body: UserCredentials):
    for stored_username in fake_users_db:
        if secrets.compare_digest(stored_username, body.username):
            raise HTTPException(status_code=409, detail="User already exists")
    fake_users_db[body.username] = {
        "username": body.username,
        "hashed_password": pwd_context.hash(body.password),
    }
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: UserCredentials):
    stored = None
    for stored_username, user_data in fake_users_db.items():
        if secrets.compare_digest(stored_username, body.username):
            stored = user_data
            break
    if stored is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(body.password, stored["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")
    return {"access_token": create_token(body.username), "token_type": "bearer"}


@app.get("/protected_resource")
def protected(username: str = Depends(verify_token)):
    return {"message": "Access granted"}
