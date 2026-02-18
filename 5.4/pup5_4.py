from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
import re

app = FastAPI(title="Headers API")


def validate_accept_language(value: str) -> bool:
    if not value:
        return False
    pattern = r'^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(\s*;\s*q\s*=\s*[0-9](\.[0-9]+)?)?(\s*,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})?(\s*;\s*q\s*=\s*[0-9](\.[0-9]+)?)?)*$'
    return bool(re.match(pattern, value.strip()))


@app.get("/headers")
async def get_headers(
    request: Request,
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None)
):
    if not user_agent:
        raise HTTPException(
            status_code=400,
            detail="Missing required header: User-Agent"
        )
    
    if not accept_language:
        raise HTTPException(
            status_code=400,
            detail="Missing required header: Accept-Language"
        )
    if not validate_accept_language(accept_language):
        raise HTTPException(
            status_code=400,
            detail="Invalid format for header: Accept-Language"
        )
    
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }


@app.get("/headers-raw")
async def get_headers_raw(request: Request):
    return {
        "User-Agent": request.headers.get("user-agent"),
        "Accept-Language": request.headers.get("accept-language"),
        "all_headers": dict(request.headers)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)