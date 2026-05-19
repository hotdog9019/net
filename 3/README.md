# Задание 3. WebSocket-комнаты для обмена сообщениями

Реализация WebSocket-чата с поддержкой комнат и HTTP-интерфейса для просмотра активных подключений.

## Запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload

# Запустить тесты
pytest
```

## WebSocket маршруты

### Подключение к комнате

```
WebSocket: /ws/rooms/{room_id}?username=alice
```

Параметры:
- `room_id` (str): название комнаты
- `username` (str): имя пользователя (обязательно)

### Сообщение от клиента

```json
{
  "type": "message",
  "text": "Hello everyone"
}
```

### Сообщение для всех пользователей комнаты

```json
{
  "type": "message",
  "room_id": "python",
  "username": "alice",
  "text": "Hello everyone"
}
```

### Событие подключения

```json
{
  "type": "user_connected",
  "username": "alice"
}
```

### Событие отключения

```json
{
  "type": "user_disconnected",
  "username": "alice"
}
```

### Ошибка (сообщение слишком длинное)

```json
{
  "type": "error",
  "detail": "Message is too long"
}
```

## HTTP маршруты

### Получить пользователей в комнате

```
GET /rooms/{room_id}/users
```

Ответ:
```json
{
  "room_id": "python",
  "users": ["alice", "bob"]
}
```

## Особенности

- Максимальная длина сообщения: 300 символов
- Имя пользователя не может быть пустым или состоять только из пробелов
- При отключении пользователя сервер уведомляет остальных
- Каждая комната изолирована - сообщения не передаются между комнатами

## Пример использования

### Python WebSocket клиент

```python
import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:8000/ws/rooms/python?username=alice"
    async with websockets.connect(uri) as websocket:
        # Receive connection event
        msg = await websocket.recv()
        print(f"Connected: {msg}")
        
        # Send message
        await websocket.send(json.dumps({
            "type": "message",
            "text": "Hello everyone!"
        }))
        
        # Receive broadcast
        msg = await websocket.recv()
        print(f"Message: {msg}")

asyncio.run(main())
```

## Структура проекта

```
12.3/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение с WebSocket маршрутами
│   ├── schemas.py           # Pydantic модели
│   └── room_manager.py      # Класс RoomManager для управления комнатами
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_websocket.py    # WebSocket тесты
├── requirements.txt
└── README.md
```

## Архитектура

### RoomManager

Класс `RoomManager` управляет WebSocket подключениями:

- `connect(room_id, username, websocket)` - добавить пользователя в комнату
- `disconnect(room_id, username)` - удалить пользователя из комнаты
- `broadcast(room_id, payload)` - отправить сообщение всем в комнате
- `get_users(room_id)` - получить список пользователей в комнате

Структура данных:
```
{
  "room_id": {
    "username1": websocket1,
    "username2": websocket2
  }
}
```

## Тесты

```bash
# Запустить все тесты
pytest

# Запустить с выводом деталей
pytest -v

# Запустить конкретный тест
pytest tests/test_websocket.py::test_websocket_send_message -v
```

Протестированные сценарии:
1. ✅ Подключение с корректным username
2. ✅ Отправка сообщения и получение ответа
3. ✅ Два клиента в одной комнате получают одно сообщение
4. ✅ Пользователи из разных комнат не получают чужие сообщения
5. ✅ Слишком длинное сообщение возвращает error
6. ✅ После отключения пользователь удаляется из списка
