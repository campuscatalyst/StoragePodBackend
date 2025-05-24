from fastapi import APIRouter
from app.core.system_manager import SystemManager
router = APIRouter()

@router.get("/harddisks")
async def get_harddisks_data():
    return SystemManager.get_harddisks_data()

@router.get("/filesystem")
async def get_filesystem_data():
    return SystemManager.get_filesystem_data()

