import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

#here we need to find a logic to find the destination dir. "/srv/dev-disk-by-uuid-09698ee9-3b6f-4504-b43d-d7b527129ac9/Folder1"

def getDestinationFolder(base_path="/srv"):
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path) and entry.startswith("dev-disk-"):
            return f"{full_path}/Folder1"
    return None

STORAGE_DIR = os.environ.get("STORAGE_DIR", getDestinationFolder())
print(STORAGE_DIR)

JSON_DIR = "/root/scripts/json"
METRICS_FILE = os.path.join(JSON_DIR, "metrics.json")
HARDDISKS_INFO_FILE = os.path.join(JSON_DIR, "hard_disks_info.json")
FILESYSTEM_INFO_FILE = os.path.join(JSON_DIR, "file_systems_info.json")
SYSTEMS_METRICS_FILE = os.path.join(JSON_DIR, "systems_metrics.json")

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()

