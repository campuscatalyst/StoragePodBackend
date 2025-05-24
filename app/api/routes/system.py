from fastapi import APIRouter
from app.core.system_manager import SystemManager
from app.api.routes.models import SystemMetrics

router = APIRouter()

@router.get("/harddisks")
async def get_harddisks_data():
    return SystemManager.get_harddisks_data()

@router.get("/filesystem")
async def get_filesystem_data():
    return SystemManager.get_filesystem_data()

@router.get("/system-metrics", response_model=SystemMetrics)
async def get_filesystem_data():
    return SystemManager.get_system_metrics()
