from typing import List
from fastapi import APIRouter, HTTPException, Query, UploadFile, Form, Body, Depends, BackgroundTasks, Request
from app.core.file_manager import FileManager
from app.api.routes.models import CreateFolderPayload
from app.core.utils import auth_utils
import json


# router = APIRouter(dependencies=[Depends(auth_utils.verify_token)])

router = APIRouter()

@router.get("/")
async def list_files(path = Query("", description="Path of the folder to be listed")):
    """
        List all files and directories in the specified path. only one level of files and folders will be returned. 
        If no path is provided, returns the empty array
    """
    return FileManager.list_directory(path)

@router.get("/metrics")
async def get_metrics():
    """
        it returns the metrics of the file explorer
    """

    return FileManager.get_metrics()

@router.post("/")
async def upload_file(request: Request,background_tasks: BackgroundTasks, path = Query("", description=""), filename = Query("", description="")):
    """
        Upload a file to the specified directory.
        If no path is provided, uploads to the root directory.
    """

    return await FileManager.upload_files_wrapper(request, background_tasks=background_tasks, path=path, filename=filename)

@router.get("/upload-progress")
async def get_upload_progress(task_id = Query("", description="task id to be monitored")):
    """
       To get progress of the upload folder
    """

    return FileManager.get_upload_progress(task_id)

@router.delete("/")
async def delete_item(path = Query("", description="Full path the file or the directory to delete")):
    """
        Delete a item/folder at the specified path
    """
    return await FileManager.delete_item(path)

@router.post("/folder")
async def create_folder(payload: CreateFolderPayload):
    """
        This will create a folder in the given path
    """

    return FileManager.create_directory(path=payload.path, directory_name=payload.folder_name)

@router.get("/download")
async def download(path = Query("", description="Path of the file or the folder to be downloaded"), inline = Query(False, description="if true it will be shown in the webview if not it will be downloaded")):
    """
       To download files/folders
       TODO - to download the folders
    """

    return FileManager.download(path, inline)

@router.post("/compress")
async def compress(background_tasks: BackgroundTasks, path = Query("", description="Path of the file or the folder to be downloaded"), ):
    """
       To compress folders
    """

    return FileManager.compress_folder(path, background_tasks)

@router.get("/compress-progress")
async def get_compress_progress(task_id = Query("", description="task id to be monitored")):
    """
       To get progress of the folder compression
    """

    return FileManager.get_progress(task_id)

@router.get("/recent-activity")
def get_recent_activity():
    """
        To get the recent activity in the Folder1 path
    """

    return FileManager.get_recent_activity()