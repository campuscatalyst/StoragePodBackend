import os, asyncio
import shutil
from datetime import datetime
from fastapi import HTTPException, BackgroundTasks, status, Request
from fastapi.responses import FileResponse, JSONResponse
from app.config import STORAGE_DIR, METRICS_FILE, RECENT_ACTIVITY_FILE
from pathlib import Path
import mimetypes
import json
import uuid
import zipfile
from typing import Dict
from app.core.utils.upload_tasks import fail_task, GLOBAL_LOCK, init_task, complete_task, get_task_status
from app.core.utils.file_utils import TrackingFileTarget, SingleFileStreamingParser
from streaming_form_data import StreamingFormDataParser

progress_store: Dict[str, int] = {}
upload_tasks: Dict[str, Dict] = {}

class FileManager:

    @staticmethod
    def validate_foldername(folder_name):
        if not folder_name:
            return False
        
        if '/' in folder_name or '\x00' in folder_name:
            return False
        
        if len(folder_name) > 255:
            return False
        
        return True
    
    @staticmethod
    def validate_path(path):
        """
            Validate and normalize the path to prevent path traversal attacks.
            path - string - path of the folder
            returns - string - normalised path
        """

        # Convert to absolute path within the storage directory
        abs_path = os.path.normpath(os.path.join(STORAGE_DIR, path.lstrip("/")))

        if not abs_path.startswith(STORAGE_DIR):
            raise HTTPException(status_code=403, detail="Access Denied")
        
        return abs_path
    
    @staticmethod
    def get_metrics():
        """
            it returns the metrics of the file explorer
        """
        try:
            if not os.path.exists(METRICS_FILE):
                return {
                    "images": 0,
                    "videos": 0,
                    "audio": 0,
                    "documents": 0,
                    "scan_time":  datetime.now()
                }
            
            with open(METRICS_FILE, "r") as f:
                data = json.load(f)

            return {
                "images": data.get("media_counts", {}).get("images", 0),
                "videos": data.get("media_counts", {}).get("videos", 0),
                "audio": data.get("media_counts", {}).get("audio", 0),
                "documents": data.get("media_counts", {}).get("documents", 0),
                "scan_time": data.get("scan_info", {}).get("date", datetime.now())
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading metrics: {str(e)}")

    @staticmethod
    def get_file_info(path, file_name):
        """
            Returns a dict of file metadata
        """

        full_path = os.path.join(path, file_name)
        stats = os.stat(full_path)

        return {
            "id": f"{stats.st_dev}-{stats.st_ino}", # here we are combining the deviceId and the inode to create a unique identifier.
            "name": file_name,
            "size": stats.st_size,
            "path": os.path.relpath(full_path, STORAGE_DIR),
            "is_directory": os.path.isdir(full_path),
            "modified_at": datetime.fromtimestamp(stats.st_mtime)
        }

    @staticmethod
    def list_directory(path):
        abs_path = FileManager.validate_path(path)
        
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=400, detail="Not a directory")
        
        items = []
        for item in os.listdir(abs_path):
            try:
                file_info = FileManager.get_file_info(abs_path, item)
                items.append(file_info)
            except Exception:
                continue

        #do the sorting if required
        #items.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
            
        rel_path = os.path.relpath(abs_path, STORAGE_DIR)
        parent_dir = os.path.dirname(rel_path) if rel_path != "." else None

        return {
            "current_path": rel_path if rel_path != "." else "",
            "files": items,
            "parent_directory": parent_dir if parent_dir else None
        }
    
    @staticmethod
    def create_directory(path, directory_name):
        """
            Create a new directory
        """
        
        abs_path = FileManager.validate_path(path)

        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="Path not found")

        if directory_name == "":
            raise HTTPException(status_code=400, detail="Directory name should not be empty")
        
        if not FileManager.validate_foldername(directory_name):
            raise HTTPException(status_code=400, detail="Invalid directory name")
        
        new_dir_path = os.path.join(abs_path, directory_name)

        if os.path.exists(new_dir_path):
            raise HTTPException(status_code=400, detail="Directory already exisits")
        
        try:
            os.makedirs(new_dir_path)
            return FileManager.get_file_info(abs_path, directory_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create directory")

    async def handle_upload(request: Request, dest_dir, task_id, filename):
        """Handle multiple large file uploads in streaming fashion"""

        try:
            content_type = request.headers.get("Content-Type", "")
            if not content_type or not content_type.startswith("multipart/form-data"):
                raise ValueError("Content-Type must be multipart/form-data for file uploads")

            parser = StreamingFormDataParser(headers=request.headers)
            await init_task(task_id, filename=filename)
            parser = SingleFileStreamingParser(request_headers=request.headers, dest_dir=dest_dir, task_id=task_id, filename=filename)
            saved_filename = await parser.parse_and_save_files(request)

            if not saved_filename:
                raise ValueError("No file was uploaded")
            
            await complete_task(task_id)

            return {"uploaded_file": saved_filename}

        except Exception as e:
            await fail_task(task_id, str(e))
            raise
    
    @staticmethod
    async def upload_files_wrapper(request: Request, background_tasks: BackgroundTasks, path: str, filename: str):
        """
            path - destination path
            file - the file that needs to be uploaded. 
        """

        if GLOBAL_LOCK.locked():
            return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Another upload is in progress") 

        abs_path = FileManager.validate_path(path)

        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=400, detail="Destination is not a directory")
        
        task_id = str(uuid.uuid4())

        try:
            result = await FileManager.handle_upload(request=request, dest_dir=abs_path, task_id=task_id, filename=filename)
            return {"task_id": task_id, "result": result}
        except Exception as e:
            await fail_task(task_id, str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_upload_progress(task_id):
        task = get_task_status(task_id=task_id)
        return task

    @staticmethod
    async def delete_item(path):
        """
            This will delete file/folder at the given path. 
        """

        abs_path = FileManager.validate_path(path)

        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="Path not found")

        try:
            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
            else:
                os.remove(abs_path)

            return {"status": "completed"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to delete the given path")
         
    @staticmethod
    def download(path, inline = False):
        """
            This will download file/folder at the given path. 
        """

        if path == "":
            raise HTTPException(status_code=400, detail="Invalid Request. Path shouldn't not be empty")

        abs_path = FileManager.validate_path(path)

        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File/Folder Path not found")
        
        if os.path.isdir(abs_path):
            raise HTTPException(status_code=400, detail="Invalid Request")
        
        file_name = os.path.basename(abs_path)
        content_type, _ = mimetypes.guess_type(file_name)

        if not content_type:
            content_type = "application/octet-stream"

        if inline and (content_type.startswith(('image/', 'application/pdf', 'text/'))):
            return FileResponse(
                path=abs_path,
                filename=file_name,
                media_type=content_type,
                content_disposition_type="inline"
            )
        
        return FileResponse(
            path=abs_path,
            filename=file_name,
            media_type=content_type
        )
    
    @staticmethod
    def zip_folder(folder_path, output_path, task_id):
        all_files = [f for f in folder_path.rglob("*") if f.is_file()]
        total_files = len(all_files)

        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for idx, file in enumerate(all_files):
                    try:
                        relative_path = file.relative_to(folder_path)
                        zipf.write(file, arcname=relative_path)
                    except Exception as file_error:
                        print(f"Failed to add {file}: {file_error}")
                    progress = int((idx + 1) / total_files * 100)
                    progress_store[task_id] = progress
            progress_store[task_id] = 100
        except Exception as e:
            print(f"Compression failed: {e}")
            progress_store[task_id] = -1

    @staticmethod
    def get_progress(task_id):
        progress = progress_store.get(task_id)

        if progress is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"task_id": task_id, "progress": progress}

    @staticmethod
    def compress_folder(path, background_tasks: BackgroundTasks):

        if path == "" or path == "/":
            raise HTTPException(status_code=404, detail="File/Folder Path not found")

        abs_path = FileManager.validate_path(path)

        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File/Folder Path not found")
        
        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=404, detail="Invalid folder path")
        
        folder_name = os.path.basename(abs_path)
        parentFolder = os.path.dirname(abs_path)
       
        output_zip = f"{parentFolder}/{folder_name}.zip"
        task_id = str(uuid.uuid4())
        progress_store[task_id] = 0

        background_tasks.add_task(FileManager.zip_folder, Path(abs_path), output_zip, task_id)

        return {"task_id": task_id, "zip_path": str(output_zip)}
    
    @staticmethod
    def get_recent_activity():
        try:
            with open(RECENT_ACTIVITY_FILE) as f:
                data = json.load(f)

            latest_by_path = {}
            for entry in data:
                path = entry["path"]
                ts = datetime.fromisoformat(entry["timestamp"])

                if path not in latest_by_path or ts > datetime.fromisoformat(latest_by_path[path]["timestamp"]):
                    latest_by_path[path] = entry

            recent = sorted(latest_by_path.values(), key=lambda e: e["timestamp"], reverse=True)
            return recent

        except FileNotFoundError:
            print("file not found")
            return []