tasks_db: dict = {}
task_counter: int = 0


def reset_storage():
    global tasks_db, task_counter
    tasks_db = {}
    task_counter = 0


def get_next_task_id():
    global task_counter
    task_counter += 1
    return task_counter
