import os
import subprocess
from fastapi import HTTPException
import json

class SystemManager:

    @staticmethod
    def get_filesystem_data():
        try:
            result = subprocess.run(
                ["omv-rpc", "-u", "admin", "FileSystemMgmt", "enumerateMountedFilesystems", '{"includeroot": true}'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )

            output = result.stdout.strip()
            data = json.loads(output)

            return {"status": "success", "data": data}
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": "Command failed",
                "stderr": e.stderr.strip()
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON output"
            }
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "message": "internal error",
            }
    @staticmethod
    def get_harddisks_data():
        try:
            result = subprocess.run(
                ["omv-rpc", "-u", "admin", "DiskMgmt", "getList", '{"start": 0, "limit": 50}'], 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )

            output = result.stdout.strip()
            data = json.loads(output)

            return {"status": "success", "data": data}
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": "Command failed",
                "stderr": e.stderr.strip()
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON output"
            }
        except Exception as e:
            print(e)
            return {
                "status": "error",
                "message": "internal error",
            }
