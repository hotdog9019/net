from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


# --- Custom exceptions ---

class CustomExceptionA(Exception):
    """Raised when a required condition is not met."""
    def __init__(self, message: str = "Condition not satisfied"):
        self.message = message


class CustomExceptionB(Exception):
    """Raised when a resource is not found."""
    def __init__(self, resource: str):
        self.message = f"Resource '{resource}' not found"


# --- Error response model ---

class ErrorResponse(BaseModel):
    error: str
    detail: str


# --- Exception handlers ---

@app.exception_handler(CustomExceptionA)
async def handle_exception_a(request: Request, exc: CustomExceptionA):
    print(f"[CustomExceptionA] {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"error": "CustomExceptionA", "detail": exc.message},
    )


@app.exception_handler(CustomExceptionB)
async def handle_exception_b(request: Request, exc: CustomExceptionB):
    print(f"[CustomExceptionB] {exc.message}")
    return JSONResponse(
        status_code=404,
        content={"error": "CustomExceptionB", "detail": exc.message},
    )


# --- In-memory storage ---

items: dict[int, str] = {1: "apple", 2: "banana"}


# --- Endpoints ---

@app.get("/check")
def check_condition(value: int):
    """Raises CustomExceptionA if value is negative."""
    if value < 0:
        raise CustomExceptionA(f"Value must be non-negative, got {value}")
    return {"message": f"Value {value} is valid"}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """Raises CustomExceptionB if item not found."""
    if item_id not in items:
        raise CustomExceptionB(f"item:{item_id}")
    return {"id": item_id, "name": items[item_id]}
