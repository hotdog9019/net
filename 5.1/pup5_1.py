from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import secrets

app = FastAPI(title="Cookie Auth API", description="API с аутентификацией на основе cookie")

class LoginRequest(BaseModel):
    username: str
    password: str
class UserProfile(BaseModel):
    username: str
    email: str
    role: str
class ErrorResponse(BaseModel):
    message: str
session_store: Dict[str, dict] = {}
USERS_DB = {
    "user123": {
        "username": "user123",
        "password": "password123",  
        "email": "user123@example.com",
        "role": "user"
    },
    "admin": {
        "username": "admin",
        "password": "admin123",
        "email": "admin@example.com",
        "role": "admin"
    }
}
async def get_current_user(session_token: Optional[str] = None):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Unauthorized"},
            headers={"WWW-Authenticate": "Cookie"},
        )
    session_data = session_store.get(session_token)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Unauthorized"},
            headers={"WWW-Authenticate": "Cookie"},
        )
    
    return session_data
@app.post("/login", response_model=UserProfile)
async def login(login_data: LoginRequest):
    username = login_data.username
    password = login_data.password
    user = USERS_DB.get(username)
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Неверное имя пользователя или пароль"}
        )
    session_token = str(uuid.uuid4())
    session_store[session_token] = {
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "token": session_token
    }
    response = JSONResponse(
        content={
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    )
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,      
        secure=True,        
        samesite="lax",    
        max_age=3600,      
        path="/"            
    )
    return response
@app.get("/user", response_model=UserProfile)
async def get_user(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"]
    }


@app.post("/logout")
async def logout(session_token: Optional[str] = None):
    if session_token and session_token in session_store:
        del session_store[session_token] 
    response = JSONResponse(content={"message": "Успешный выход"})
    response.delete_cookie(key="session_token", path="/")
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}