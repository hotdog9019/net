import pytest


def test_websocket_connect_with_valid_username(client):
    """Test WebSocket connection with valid username."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        # Should receive user_connected event
        data = websocket.receive_json()
        assert data["type"] == "user_connected"
        assert data["username"] == "alice"


def test_websocket_connect_without_username(client):
    """Test WebSocket connection without username."""
    with pytest.raises(Exception):
        client.websocket_connect("/ws/rooms/python")


def test_websocket_send_message(client):
    """Test sending a message through WebSocket."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        # Receive user_connected event
        websocket.receive_json()
        
        # Send message
        websocket.send_json({"type": "message", "text": "Hello everyone"})
        
        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "message"
        assert data["room_id"] == "python"
        assert data["username"] == "alice"
        assert data["text"] == "Hello everyone"


def test_multiple_clients_same_room(client):
    """Test two clients in the same room receive the same message."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_alice:
        # Alice receives user_connected event
        ws_alice.receive_json()
        
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws_bob:
            # Alice receives bob_connected event
            data = ws_alice.receive_json()
            assert data["type"] == "user_connected"
            assert data["username"] == "bob"
            
            # Bob receives alice_connected (already connected) + bob_connected
            ws_bob.receive_json()  # alice_connected
            ws_bob.receive_json()  # bob_connected
            
            # Alice sends message
            ws_alice.send_json({"type": "message", "text": "Hi Bob"})
            
            # Both receive the message
            alice_msg = ws_alice.receive_json()
            bob_msg = ws_bob.receive_json()
            
            assert alice_msg["text"] == "Hi Bob"
            assert bob_msg["text"] == "Hi Bob"
            assert alice_msg["username"] == "alice"
            assert bob_msg["username"] == "alice"


def test_different_rooms_isolation(client):
    """Test that users in different rooms don't receive each other's messages."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_python:
        ws_python.receive_json()  # user_connected
        
        with client.websocket_connect("/ws/rooms/javascript?username=bob") as ws_js:
            ws_js.receive_json()  # user_connected
            
            # Alice sends message in python room
            ws_python.send_json({"type": "message", "text": "Python message"})
            
            # Alice receives her message
            python_msg = ws_python.receive_json()
            assert python_msg["text"] == "Python message"
            
            # Bob should not receive it (no message received)
            # We can verify by checking no new messages in the queue
            # Since we're using receive_json, we'd get a timeout if nothing is there
            try:
                ws_js.receive_json(timeout=0.1)
                pytest.fail("Should not receive message from different room")
            except Exception:
                # Expected - no message received
                pass


def test_message_too_long(client):
    """Test that messages longer than 300 characters return an error."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()  # user_connected
        
        # Send message longer than 300 characters
        long_message = "a" * 301
        websocket.send_json({"type": "message", "text": long_message})
        
        # Receive error response
        error = websocket.receive_json()
        assert error["type"] == "error"
        assert "too long" in error["detail"].lower()


def test_get_room_users(client):
    """Test getting users list from a room."""
    # No users yet
    response = client.get("/rooms/python/users")
    assert response.status_code == 200
    assert response.json() == {"room_id": "python", "users": []}
    
    # Connect Alice
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_alice:
        ws_alice.receive_json()  # user_connected
        
        # Check users list
        response = client.get("/rooms/python/users")
        data = response.json()
        assert data["room_id"] == "python"
        assert data["users"] == ["alice"]
        
        # Connect Bob
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws_bob:
            ws_bob.receive_json()  # user_connected
            ws_alice.receive_json()  # user_connected for bob
            
            # Check users list
            response = client.get("/rooms/python/users")
            data = response.json()
            assert set(data["users"]) == {"alice", "bob"}
        
        # Bob disconnected
        response = client.get("/rooms/python/users")
        data = response.json()
        assert data["users"] == ["alice"]


def test_websocket_disconnect_broadcasts_event(client):
    """Test that disconnection broadcasts user_disconnected event."""
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws_alice:
        ws_alice.receive_json()  # user_connected
        
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws_bob:
            ws_bob.receive_json()  # user_connected
            ws_alice.receive_json()  # bob user_connected
            
            # Bob disconnects
        
        # Alice should receive user_disconnected event
        data = ws_alice.receive_json()
        assert data["type"] == "user_disconnected"
        assert data["username"] == "bob"


def test_websocket_invalid_username(client):
    """Test that empty username is rejected."""
    # Try with empty string
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/python?username=") as ws:
            pass
    
    # Try with only whitespace
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/python?username=   ") as ws:
            pass
