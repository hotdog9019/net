from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

app = FastAPI()


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя")
    email: EmailStr = Field(..., description="Адрес электронной почты")
    age: Optional[int] = Field(None, ge=1, description="Возраст пользователя")
    is_subscribed: bool = Field(False, description="Подписка на новостную рассылку")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Имя не может быть пустым')
        return v.strip()


class UserResponse(BaseModel):
    name: str
    email: str
    age: Optional[int]
    is_subscribed: bool
    message: str


@app.post("/create_user", response_model=UserResponse)
async def create_user(user: UserCreate):
    """
    Создает нового пользователя на основе предоставленных данных.
    """
    return UserResponse(
        name=user.name,
        email=user.email,
        age=user.age,
        is_subscribed=user.is_subscribed,
        message="Пользователь успешно создан"
    )