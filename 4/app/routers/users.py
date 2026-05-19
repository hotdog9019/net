from fastapi import APIRouter, Depends
from app.schemas import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user information."""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> User:
    """Get user information by ID."""
    # In real app, would fetch from database
    # For now, just return a mock user
    return User(id=user_id, role="user")
