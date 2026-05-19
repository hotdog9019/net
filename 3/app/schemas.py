from typing import Literal
from pydantic import BaseModel


class MessagePayload(BaseModel):
    type: Literal["message"]
    text: str


class ErrorPayload(BaseModel):
    type: Literal["error"]
    detail: str


class BroadcastMessage(BaseModel):
    type: Literal["message"]
    room_id: str
    username: str
    text: str


class UserConnectedPayload(BaseModel):
    type: Literal["user_connected"]
    username: str


class UserDisconnectedPayload(BaseModel):
    type: Literal["user_disconnected"]
    username: str


class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]
