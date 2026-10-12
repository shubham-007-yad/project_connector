from sqlalchemy.orm import Session

from .db_models import TaskDB
from .models import Task


def get_tasks(db: Session) -> list[TaskDB]:
    return db.query(TaskDB).all()


def create_task(db: Session, task: Task) -> TaskDB:
    db_task = TaskDB(
        id=task.id,
        title=task.title,
        completed=task.completed
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

def update_task(db: Session, task_id: int, task: Task) -> TaskDB | None:
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if db_task is None:
        return None

    db_task.title = task.title
    db_task.completed = task.completed

    db.commit()
    db.refresh(db_task)

    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if db_task is None:
        return False

    db.delete(db_task)
    db.commit()

    return True

def get_task(db: Session, task_id: int) -> TaskDB | None:
    return db.query(TaskDB).filter(TaskDB.id == task_id).first()