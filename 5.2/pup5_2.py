from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import uuid

app = FastAPI()
SECRET_KEY = "anys"
serializer = URLSafeTimedSerializer(SECRET_KEY)
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

@app.post("/login")
async def login(data: LoginRequest):
    user = USERS_DB.get(data.username)
    
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    token = serializer.dumps(user["user_id"])

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,      
        max_age=3600,       
        samesite="lax"
    )
    return response

@app.get("/profile")
async def get_profile(request: Request):
    token = request.cookies.get("session_token")
    
    if not token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    try:
        user_id = serializer.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})


    for user in USERS_DB.values():
        if user["user_id"] == user_id:
            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"]
            }

    raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)