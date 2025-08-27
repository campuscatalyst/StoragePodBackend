import asyncio
from sqlmodel import Session, select
from app.db.models import UploadTask
from datetime import datetime, timedelta, timezone

UPLOAD_SEMAPHORE = asyncio.Semaphore(3)  # max 3 parallel uploads

async def init_task(session: Session, task_id: str, filename: str):
    task = UploadTask(task_id=task_id, filename=filename, status="uploading")
    session.add(task)
    session.commit()

async def update_progress(session: Session, task_id: str, written: int, total: int):
    task = session.get(UploadTask, task_id)
    if task and task.status == "uploading":
        task.written = written
        task.total = total
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

async def complete_task(session: Session, task_id: str):
    task = session.get(UploadTask, task_id)
    if task:
        task.status = "done"
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

async def fail_task(session: Session, task_id: str, error: str):
    task = session.get(UploadTask, task_id)
    if task:
        task.status = "failed"
        task.error = error
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

def get_task_status(session: Session, task_id: str) -> dict:
    task = session.get(UploadTask, task_id)
    if not task:
        return {"status": "not_found"}
    return task.model_dump()

async def cleanup_old_uploads(session: Session):
    old_tasks = session.exec(
        select(UploadTask).where(UploadTask.created_at < datetime.now(timezone.utc) - timedelta(days=1))
    ).all()

    for task in old_tasks:
        session.delete(task)
    session.commit()
