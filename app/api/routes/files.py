from typing import List
from fastapi import APIRouter, HTTPException, Query, UploadFile, Form, Body, Depends, BackgroundTasks, Request
from app.core.file_manager import FileManager
from app.api.routes.models import CreateFolderPayload, RenameItemRequest, MoveItemRequest, CopyItemRequest
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

    return await FileManager.start_upload(request, background_tasks=background_tasks, path=path, filename=filename)

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

@router.patch("/rename")
def rename_item(rename_payload: RenameItemRequest):
    """
        This will rename the given file/folder to the given new name
    """

    return FileManager.rename_item(rename_payload.path, rename_payload.is_directory, rename_payload.new_name)

@router.post("/move")
def move_item(move_payload: MoveItemRequest):
    """
        This will move the given file/folder to the given dst folder
    """

    return FileManager.move_item(move_payload.path, move_payload.dst_path)

@router.post("/copy")
def move_item(copy_payload: CopyItemRequest):
    """
        This will move the given file/folder to the given dst folder
    """

    return FileManager.copy_item(copy_payload.path, copy_payload.dst_path)

@router.get("/search")
def search(
    query: str = Query(..., description="The keyword that the user wants to search"),
    type: str | None  = Query(default=None, description="To search file/folder"),
    sort: str | None = Query(default=None, description="The field that user wants to sort"),
    order: str | None = Query(default=None, description="asc/dsc sort the result"),
    limit: str | None = Query(default=None, description="Limit to the number of results")
):
    """
        This is a global search function, which will search the entire Folder1 contents. 
    """
    
    return FileManager.search(q=query, type=type, sort=sort, order=order, limit=limit)