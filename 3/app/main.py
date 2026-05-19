from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from app.room_manager import room_manager
from app.schemas import RoomUsersResponse

app = FastAPI()

MAX_MESSAGE_LENGTH = 300


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(room_id: str, websocket: WebSocket, username: str = Query(...)):
    """WebSocket endpoint for chat rooms."""
    # Validate username
    if not username or not username.strip():
        await websocket.accept()
        await websocket.close(code=1008, reason="Invalid username")
        return
    
    username = username.strip()
    
    # Connect user
    await room_manager.connect(room_id, username, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                text = data.get("text", "")
                
                # Check message length
                if len(text) > MAX_MESSAGE_LENGTH:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Message is too long"
                    })
                    continue
                
                # Broadcast message to all users in room
                await room_manager.broadcast(
                    room_id,
                    {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    }
                )
    
    except WebSocketDisconnect:
        await room_manager.disconnect(room_id, username)


@app.get("/rooms/{room_id}/users", response_model=RoomUsersResponse)
def get_room_users(room_id: str):
    """Get list of users in a room."""
    users = room_manager.get_users(room_id)
    return RoomUsersResponse(room_id=room_id, users=users)
