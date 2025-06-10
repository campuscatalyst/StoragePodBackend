import asyncio
import time

upload_tasks = {}
task_timestamps = {}
GLOBAL_LOCK = asyncio.Lock()
TASK_EXPIRY_SECONDS = 120  # Auto-clean after 2 min

def is_upload_in_progress():
    # this will check if there is any task with status as uploading in upload_tasks. if so it will return true else false.
    return any(task.get("status") == "uploading" for task in upload_tasks.values())

async def init_task(task_id, filename):
    upload_tasks[task_id] = {
        "status": "uploading",
        "filename": filename,
        "progress": {"written": 0, "total": 0}
    }

    task_timestamps[task_id] = time.time()

async def update_progress(task_id, written, total):
    task = upload_tasks.get(task_id)
    if task and task["status"] == "uploading":
        task["progress"]["written"] = written
        task["progress"]["total"] = total

async def complete_task(task_id):
    if task_id in upload_tasks:
        upload_tasks[task_id]["status"] = "done"

async def fail_task(task_id, error):
    if task_id in upload_tasks:
        upload_tasks[task_id]["status"] = "failed"
        upload_tasks[task_id]["error"] = str(error)

def get_task_status(task_id):
    now = time.time()
    if task_id in task_timestamps and (now - task_timestamps[task_id] > TASK_EXPIRY_SECONDS):
        upload_tasks.pop(task_id, None)
        task_timestamps.pop(task_id, None)
        return {"status": "expired"}
    
    return upload_tasks.get(task_id, {"status": "not_found"})
