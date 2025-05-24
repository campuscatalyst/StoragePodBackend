import os
import subprocess
from fastapi import HTTPException
import json
from app.config import HARDDISKS_INFO_FILE, FILESYSTEM_INFO_FILE

class SystemManager:

    @staticmethod
    def get_filesystem_data():
        try:
            with open(HARDDISKS_INFO_FILE, "r") as f:
                data = json.load(f)
            
            return {"status": "success", "data": data}
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "message": "internal error",
            }
    @staticmethod
    def get_harddisks_data():
        try:
            with open(FILESYSTEM_INFO_FILE, "r") as f:
                data = json.load(f)
            
            return {"status": "success", "data": data}
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "message": "internal error",
            }
