from fastapi import WebSocket


class RoomManager:
    def __init__(self):
        # Structure: {room_id: {username: websocket}}
        self.rooms: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        """Add a user to a room."""
        await websocket.accept()
        
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][username] = websocket
        
        # Broadcast user connected event
        await self.broadcast(
            room_id,
            {"type": "user_connected", "username": username}
        )

    async def disconnect(self, room_id: str, username: str):
        """Remove a user from a room."""
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            
            # Broadcast user disconnected event
            await self.broadcast(
                room_id,
                {"type": "user_disconnected", "username": username}
            )
            
            # Clean up empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        """Send message to all users in a room."""
        if room_id not in self.rooms:
            return
        
        for websocket in self.rooms[room_id].values():
            try:
                await websocket.send_json(payload)
            except Exception:
                # Silently ignore disconnected clients
                pass

    def get_users(self, room_id: str) -> list[str]:
        """Get list of users in a room."""
        if room_id not in self.rooms:
            return []
        return list(self.rooms[room_id].keys())


# Global room manager instance
room_manager = RoomManager()
