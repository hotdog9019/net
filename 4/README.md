# Задание 4. Внедрение зависимостей и расширенная маршрутизация

Модульная архитектура FastAPI приложения с использованием `APIRouter`, зависимостей и проверки прав доступа.

## Запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload

# Запустить тесты
pytest

# Запустить Swagger UI
# Откройте http://localhost:8000/docs
```

## Архитектура

### Структура проекта

```
12.4/
├── app/
│   ├── __init__.py
│   ├── main.py              # Основное приложение
│   ├── dependencies.py      # Зависимости
│   ├── schemas.py           # Pydantic модели
│   ├── storage.py           # Хранилище в памяти
│   └── routers/
│       ├── __init__.py
│       ├── tasks.py         # Маршруты для задач
│       ├── users.py         # Маршруты для пользователей
│       └── admin.py         # Админские маршруты
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_dependencies_and_routing.py
├── requirements.txt
└── README.md
```

## Зависимости

### `get_current_user`

Извлекает информацию о пользователе из заголовков:
- `X-User-Id` (обязательно) - ID пользователя
- `X-User-Role` (опционально, по умолчанию "user") - роль пользователя

Возвращает объект `User`:
```json
{"id": 10, "role": "user"}
```

Возвращает `401`, если `X-User-Id` отсутствует или некорректен.

### `require_admin`

Зависимость для проверки роли администратора. Использует `get_current_user` и проверяет, что `role == "admin"`.

Возвращает `403`, если роль не `admin`.

### `get_storage`

Возвращает словарь хранилища задач.

## API маршруты

### Tasks (`/tasks`, tag: "tasks")

- `POST /tasks` - создать задачу
- `GET /tasks` - получить список задач текущего пользователя
- `GET /tasks/{task_id}` - получить задачу по ID
- `PATCH /tasks/{task_id}/status` - обновить статус
- `DELETE /tasks/{task_id}` - удалить задачу

### Users (`/users`, tag: "users")

- `GET /users/me` - получить информацию текущего пользователя
- `GET /users/{user_id}` - получить информацию пользователя по ID

### Admin (`/admin`, tag: "admin")

- `GET /admin/stats` - получить статистику по всем задачам (только для админов)
- `DELETE /admin/tasks/{task_id}` - удалить любую задачу (только для админов)

## Примеры запросов

### Как обычный пользователь

```bash
# Получить свою информацию
curl -X GET http://localhost:8000/users/me \
  -H "X-User-Id: 10" \
  -H "X-User-Role: user"

# Создать задачу
curl -X POST http://localhost:8000/tasks \
  -H "X-User-Id: 10" \
  -H "X-User-Role: user" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My task",
    "status": "todo",
    "priority": 3
  }'

# Получить свои задачи
curl -X GET http://localhost:8000/tasks \
  -H "X-User-Id: 10" \
  -H "X-User-Role: user"
```

### Как администратор

```bash
# Получить статистику
curl -X GET http://localhost:8000/admin/stats \
  -H "X-User-Id: 20" \
  -H "X-User-Role: admin"

# Удалить чужую задачу
curl -X DELETE http://localhost:8000/admin/tasks/1 \
  -H "X-User-Id: 20" \
  -H "X-User-Role: admin"
```

## Swagger UI

Все маршруты сгруппированы по тегам:
- **tasks** - управление задачами
- **users** - информация о пользователях
- **admin** - административные функции

Откройте http://localhost:8000/docs для просмотра всех маршрутов.

## Тесты

```bash
# Запустить все тесты
pytest

# Запустить с выводом деталей
pytest -v

# Запустить конкретный тест
pytest tests/test_dependencies_and_routing.py::test_admin_access_to_stats -v
```

Протестированные сценарии:
1. ✅ `/users/me` возвращает текущего пользователя
2. ✅ Пользователь без `X-User-Id` получает 401
3. ✅ Обычный пользователь получает 403 при обращении к `/admin/stats`
4. ✅ Администратор получает статистику по всем задачам
5. ✅ Обычный пользователь не может удалить чужую задачу
6. ✅ Администратор может удалить чужую задачу через `/admin/tasks/{task_id}`
7. ✅ Swagger UI группирует маршруты по тегам

## Особенности

- Все маршруты `/tasks` требуют аутентификацию через `get_current_user`
- Все маршруты `/admin` требуют роль `admin` через `require_admin`
- Пользователи видят только свои задачи
- Администраторы могут управлять всеми задачами
- Маршруты сгруппированы по смыслу и имеют теги для Swagger UI
