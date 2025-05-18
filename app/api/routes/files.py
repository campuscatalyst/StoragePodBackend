from typing import List
from fastapi import APIRouter, HTTPException, Query, UploadFile, Form, Body, Depends
from app.core.file_manager import FileManager
from app.core.utils import auth_utils

router = APIRouter(dependencies=[Depends(auth_utils.verify_token)])

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
async def upload_file(files: List[UploadFile], path = Form("", description="")):
    """
        Upload a file to the specified directory.
        If no path is provided, uploads to the root directory.
    """
    response_details = []
    for file in files:
        response_details.append(await FileManager.upload_file(path, file))

    return response_details

@router.delete("/")
async def delete_item(path = Query("", description="Full path the file or the directory to delete")):
    """
        Delete a item/folder at the specified path
    """
    return await FileManager.delete_item(path)

@router.post("/folder")
async def create_folder(path = Body(""), folderName = Body("")):
    """
        This will create a folder in the given path
    """

    return FileManager.create_directory(path, folderName)

@router.get("/download")
async def download(path = Query("", description="Path of the file or the folder to be downloaded"), inline = Query(False, description="if true it will be shown in the webview if not it will be downloaded")):
    """
       To download files/folders
       TODO - to download the folders
    """

    return FileManager.download(path, inline)


