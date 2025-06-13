import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

def getDestinationFolder(base_path="/srv"):
    try:
        for entry in os.listdir(base_path):
            full_path = os.path.join(base_path, entry)
            if os.path.isdir(full_path) and entry.startswith("dev-disk-"):
                return f"{full_path}/Folder1"
        return None
    except FileNotFoundError:
        return None

STORAGE_DIR = os.environ.get("STORAGE_DIR", getDestinationFolder())

JSON_DIR = "/root/scripts/json"
METRICS_FILE = os.path.join(JSON_DIR, "metrics.json")
HARDDISKS_INFO_FILE = os.path.join(JSON_DIR, "hard_disks_info.json")
SMART_INFO_FILE = os.path.join(JSON_DIR, "smart_info.json")
FILESYSTEM_INFO_FILE = os.path.join(JSON_DIR, "file_systems_info.json")
SYSTEMS_METRICS_FILE = os.path.join(JSON_DIR, "systems_metrics.json")

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()

