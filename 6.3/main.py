import secrets
import os
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")

if MODE not in ("DEV", "PROD"):
    raise ValueError(f"Invalid MODE='{MODE}'. Must be DEV or PROD.")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_users_db: dict[str, dict] = {}


def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = fake_users_db.get(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    username_ok = secrets.compare_digest(credentials.username, user["username"])
    password_ok = pwd_context.verify(credentials.password, user["hashed_password"])
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def check_docs_auth(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )
    import base64
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})
    if not (secrets.compare_digest(username, DOCS_USER) and secrets.compare_digest(password, DOCS_PASSWORD)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})


if MODE == "DEV":
    @app.get("/docs", include_in_schema=False)
    def custom_docs(request: Request):
        check_docs_auth(request)
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

    @app.get("/openapi.json", include_in_schema=False)
    def custom_openapi(request: Request):
        check_docs_auth(request)
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

else:
    @app.get("/docs", include_in_schema=False)
    @app.get("/openapi.json", include_in_schema=False)
    @app.get("/redoc", include_in_schema=False)
    def hidden_docs():
        raise HTTPException(status_code=404)


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": pwd_context.hash(user.password),
    }
    return {"message": f"User '{user.username}' registered successfully"}


@app.get("/login")
def login(username: str = Depends(auth_user)):
    return {"message": f"Welcome, {username}!"}
