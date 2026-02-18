from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Annotated
import re

app = FastAPI(title="Headers API v2")

class CommonHeaders(BaseModel):
    user_agent: Annotated[str, Header(...)]
    accept_language: Annotated[str, Header(...)]

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        if not value:
            raise ValueError("Accept-Language cannot be empty")
        pattern = r'^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(\s*;\s*q\s*=\s*[0-9](\.[0-9]+)?)?(\s*,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(\s*;\s*q\s*=\s*[0-9](\.[0-9]+)?)?)*$'
        
        if not re.match(pattern, value.strip()):
            raise ValueError(
                f"Invalid Accept-Language format: '{value}'. "
                f"Expected format like: 'en-US,en;q=0.9,es;q=0.8'"
            )
        return value

@app.get("/headers")
async def get_headers(headers: CommonHeaders):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/info")
async def get_info(headers: CommonHeaders, response: Response):
    server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    response.headers["X-Server-Time"] = server_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }

@app.get("/debug-headers")
async def debug_headers(headers: CommonHeaders):
    return {
        "model_dump": headers.model_dump(),
        "user_agent_type": type(headers.user_agent).__name__,
        "accept_language_type": type(headers.accept_language).__name__
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)