import os
import subprocess
from fastapi import HTTPException
import json
from app.config import HARDDISKS_INFO_FILE, FILESYSTEM_INFO_FILE, SYSTEMS_METRICS_FILE, SMART_INFO_FILE
from app.api.routes.models import LoadAverage, SystemMetrics
from app.logger import logger

class SystemManager:

    @staticmethod
    def get_filesystem_data():
        try:
            with open(FILESYSTEM_INFO_FILE, "r") as f:
                data = json.load(f)
            
            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f'Exception occurred while retrieving file system data: {e}')
            raise HTTPException(500, detail="Internal Error")
    
    @staticmethod
    def get_harddisks_data():
        try:
            with open(HARDDISKS_INFO_FILE, "r") as f:
                data = json.load(f)
            
            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f'Exception occurred while retrieving hard disks data: {e}')
            raise HTTPException(500, detail="Internal Error")
    
    @staticmethod
    def get_smart_info():
        try:
            with open(SMART_INFO_FILE, "r") as f:
                data = json.load(f)
            
            return {"status": "success", "data": data}
        except Exception as e:
            logger.error(f'Exception occurred while retrieving smart info data: {e}')
            raise HTTPException(500, detail="Internal Error")

    @staticmethod
    def get_system_metrics():
        try:
            with open(SYSTEMS_METRICS_FILE, "r") as f:
                data = json.load(f)
            
            mem_util_percent = (int(data.get("memUsed", "0")) / int(data.get("memTotal", "1"))) * 100

            return SystemMetrics(
                timestamp=data["ts"],
                hostname=data["hostname"],
                version=data["version"],
                cpu_model=data["cpuModelName"],
                cpu_utilization_percent=data["cpuUtilization"],
                memory_utilization_percent=mem_util_percent,
                load_average=LoadAverage(
                    min1=data["loadAverage"]["1min"],
                    min5=data["loadAverage"]["5min"],
                    min15=data["loadAverage"]["15min"],
                ),
                uptime_seconds=data["uptime"],
                available_package_updates=data["availablePkgUpdates"]
            )
        except Exception as e:
            logger.error(f'Exception occurred while retrieving system metrics data: {e}')
            raise HTTPException(500, detail="Internal Error")
