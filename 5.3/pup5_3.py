from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import uuid
import time

app = FastAPI()


SECRET_KEY = "anys2"
SALT = "session-salt"
COOKIE_NAME = "session_token"
SESSION_MAX_AGE = 300  
RENEW_THRESHOLD = 180  

serializer = URLSafeTimedSerializer(SECRET_KEY, salt=SALT)


USERS_DB = {
    "user123": {
        "username": "user123",
        "password": "password123",
        "user_id": str(uuid.uuid4()),
        "email": "user123@example.com"
    },
    "admin": {
        "username": "admin",
        "password": "admin123",
        "user_id": str(uuid.uuid4()),
        "email": "admin@example.com"
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str


def create_session_token(user_id: str, timestamp: int) -> str:
    data = {"user_id": user_id, "timestamp": timestamp}
    return serializer.dumps(data)


def verify_session_token(token: str) -> dict:
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        if "user_id" not in data or "timestamp" not in data:
            raise ValueError("Invalid token structure")
        return data
    except SignatureExpired:
        raise HTTPException(status_code=401, detail={"message": "Session expired"})
    except BadSignature:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})


def get_user_by_id(user_id: str) -> dict:
    for user in USERS_DB.values():
        if user["user_id"] == user_id:
            return user
    return None


def create_cookie_response(content: dict, token: str, renew: bool = False) -> JSONResponse:
    response = JSONResponse(content=content)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/"
    )
    return response

@app.post("/login")
async def login(data: LoginRequest):
    user = USERS_DB.get(data.username)
    
    if not user or user["password"] != data.password:
        response = JSONResponse(
            status_code=401,
            content={"message": "Invalid credentials"}
        )
        return response

    current_time = int(time.time())
    token = create_session_token(user["user_id"], current_time)
    
    return create_cookie_response(
        content={
            "message": "Login successful",
            "user_id": user["user_id"],
            "username": user["username"]
        },
        token=token
    )


@app.get("/profile")
async def get_profile(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    
    if not token:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )
    token_data = verify_session_token(token)
    user_id = token_data["user_id"]
    last_activity = token_data["timestamp"]
    current_time = int(time.time())
    user = get_user_by_id(user_id)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid session"}
        )
    time_since_activity = current_time - last_activity
    if time_since_activity > SESSION_MAX_AGE:
        return JSONResponse(
            status_code=401,
            content={"message": "Session expired"}
        )

    if time_since_activity >= RENEW_THRESHOLD:
        new_token = create_session_token(user_id, current_time)
        return create_cookie_response(
            content={
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "session_renewed": True
            },
            token=new_token,
            renew=True
        )
    else:
        return JSONResponse(
            content={
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "session_renewed": False
            }
        )


@app.get("/check-session")
async def check_session(request: Request):
    """Проверка статуса сессии без обновления"""
    token = request.cookies.get(COOKIE_NAME)
    
    if not token:
        return JSONResponse(status_code=401, content={"valid": False, "message": "No session"})

    try:
        token_data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        current_time = int(time.time())
        time_since_activity = current_time - token_data["timestamp"]
        
        return {
            "valid": True,
            "time_since_activity": time_since_activity,
            "expires_in": SESSION_MAX_AGE - time_since_activity
        }
    except:
        return JSONResponse(status_code=401, content={"valid": False, "message": "Invalid session"})


@app.post("/logout")
async def logout():
    """Выход из системы"""
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



    