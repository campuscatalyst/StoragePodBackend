from fastapi import HTTPException
from tuspyserver.router import create_tus_router
from app.config import TEMP_UPLOADS_DIR

def on_upload_complete(file_path: str, metadata: dict):
    print("Upload complete")
    print(file_path)
    print(metadata)

def pre_create_hook(metadata: dict, upload_info: dict):
    if "filename" not in metadata:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if "path" not in metadata:
        raise HTTPException(status_code=400, detail="Upload Path is required")

router = create_tus_router(
    files_dir=TEMP_UPLOADS_DIR,
    max_size=1024 * 1024 * 1024 * 1024, # 1 TB max upload size
    days_to_keep=1,
    on_upload_complete=on_upload_complete,
    pre_create_hook=pre_create_hook,
    prefix="/api/v1/uploads"
)



