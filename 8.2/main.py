from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_db_connection, init_db

app = FastAPI()
init_db()


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


def row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


@app.post("/todos", status_code=201)
def create_todo(body: TodoCreate):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description) VALUES (?, ?)",
        (body.title, body.description),
    )
    conn.commit()
    todo_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return row_to_dict(row)


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, body: TodoUpdate):
    conn = get_db_connection()
    result = conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (body.title, body.description, int(body.completed), todo_id),
    )
    conn.commit()
    if result.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    result = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
