import os
import shutil
from datetime import datetime
from fastapi import HTTPException
from app.config import STORAGE_DIR

class FileManager:
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
        print(path, directory_name)

        abs_path = FileManager.validate_path(path)
        new_dir_path = os.path.join(abs_path, directory_name)

        if os.path.exists(new_dir_path):
            raise HTTPException(status_code=400, detail="Directory already exisits")
        
        try:
            os.makedirs(new_dir_path)
            return FileManager.get_file_info(abs_path, directory_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create directory")
        
    @staticmethod
    async def upload_file(path, file):
        """
            path - destination path
            file - the file that needs to be uploaded. 
        """

        print(file)
        abs_path = FileManager.validate_path(path)

        if not os.path.isdir(abs_path):
            raise HTTPException(status_code=400, detail="Destination is not a directory")
        
        # add file extension logic here if needed, to restrict/allow file extensions

        file_path = os.path.join(abs_path, file.filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return FileManager.get_file_info(abs_path, file.filename)
        except Exception as e:
             raise HTTPException(status_code=500, detail="Failed to upload your file")
        finally:
            file.file.close()

    @staticmethod
    async def delete_item(path):
        """
            This will delete file/folder at the given path. 
        """

        abs_path = FileManager.validate_path(path)
        print(abs_path)

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
         