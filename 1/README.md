# Задание 1. Интеграционные тесты для API задач

Приложение FastAPI для управления задачами пользователя с интеграционными тестами.

## Установка и запуск

### Локально

```bash
# Создать виртуальное окружение
python -m venv .venv

# Активировать окружение (Windows)
.venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
uvicorn app.main:app --reload

# Запустить тесты
pytest
```

Сервер будет доступен по адресу: `http://localhost:8000`

Документация API: `http://localhost:8000/docs`

## API Маршруты

- `POST /tasks` - создать новую задачу (код 201)
- `GET /tasks` - получить список задач текущего пользователя
- `GET /tasks/{task_id}` - получить задачу по ID
- `PATCH /tasks/{task_id}/status` - обновить статус задачи
- `DELETE /tasks/{task_id}` - удалить задачу (код 204)

## Аутентификация

Все запросы требуют заголовок `X-User-Id`:

```
X-User-Id: 10
```

## Примеры запросов

### Создание задачи

```bash
curl -X POST http://localhost:8000/tasks \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Подготовить тесты",
    "description": "Написать интеграционные тесты",
    "status": "todo",
    "priority": 4
  }'
```

### Получение задач

```bash
curl -X GET http://localhost:8000/tasks \
  -H "X-User-Id: 10"
```

### Получение задач с фильтрацией

```bash
curl -X GET "http://localhost:8000/tasks?status=done&min_priority=2" \
  -H "X-User-Id: 10"
```

### Обновление статуса

```bash
curl -X PATCH http://localhost:8000/tasks/1/status \
  -H "X-User-Id: 10" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Удаление задачи

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "X-User-Id: 10"
```

## Тесты

Все тесты находятся в папке `tests/`.

```bash
# Запустить все тесты
pytest

# Запустить с выводом деталей
pytest -v

# Запустить конкретный тест
pytest tests/test_tasks.py::test_create_task_success -v
```

## Структура проекта

```
12.1/
├── app/
│   ├── __init__.py
│   ├── main.py           # Основное приложение FastAPI
│   ├── schemas.py        # Pydantic модели
│   └── storage.py        # Хранилище в памяти
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Фикстуры для тестов
│   └── test_tasks.py     # Интеграционные тесты
├── requirements.txt
└── README.md
```
