# Задание 2. Docker-контейнеризация FastAPI-приложения

Упаковка FastAPI-приложения для управления задачами в Docker-контейнер с использованием `docker compose`.

## Локальный запуск

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

## Docker запуск

### Сборка и запуск контейнера

```bash
docker compose up --build
```

### Проверка приложения

```bash
# Health check
curl http://localhost:8000/health

# Получить список задач
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

### Остановка контейнера

```bash
docker compose down
```

## Структура проекта

```
12.2/
├── app/
│   ├── __init__.py
│   ├── main.py           # Основное приложение с /health
│   ├── schemas.py        # Pydantic модели
│   └── storage.py        # Хранилище в памяти
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_tasks.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── README.md
```

## Docker детали

### Dockerfile

- Базовый образ: `python:3.12-slim`
- Рабочая директория: `/app`
- Порт: `8000`
- Команда запуска: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### docker-compose.yml

- Сервис `api` собирается из текущей директории
- Пробросывает порт `8000:8000`
- Переменная окружения: `APP_ENV=docker`
- Политика перезапуска: `unless-stopped`

## API маршруты

- `GET /health` - проверка состояния приложения
- `POST /tasks` - создать новую задачу
- `GET /tasks` - получить список задач
- `GET /tasks/{task_id}` - получить задачу по ID
- `PATCH /tasks/{task_id}/status` - обновить статус
- `DELETE /tasks/{task_id}` - удалить задачу

## Примеры запросов

### Health check

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{"status": "ok", "env": "docker"}
```

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

Ответ для пустого списка:
```json
[]
```
