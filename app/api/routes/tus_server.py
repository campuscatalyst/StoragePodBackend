import os, shutil
from fastapi import HTTPException
from tuspyserver.router import create_tus_router
from app.config import TEMP_UPLOADS_DIR
from app.core.file_manager import FileManager
from app.logger import logger

def on_upload_complete(file_path: str, metadata: dict):
    try:
        target_dir = metadata.get("path")
        filename = metadata.get("filename")

        if not target_dir or not filename:
            raise HTTPException(status_code=400, detail="Invalid metadata: path or filename missing")

        abs_path = FileManager.validate_path(target_dir)

        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=400, detail="Destination is not a directory")
        
        if not FileManager.validate_itemname(filename):
            raise HTTPException(status_code=400, detail="Invalid filename provided")
        
        destination = os.path.join(target_dir, filename)

        try:
            # Move the file from temp to destination
            logger.info(f"Moving file from {abs_path} to {destination}")
            shutil.move(abs_path, destination)
            logger.info("Moving completed!")
        except Exception as e:
            logger.error(f"Failed to move file: {str(e)}")
            raise
        
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logger.error(f"Error while uploading the file - {str(e)}")
        return HTTPException(status_code=500, detail=f"{str(e)}")

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



