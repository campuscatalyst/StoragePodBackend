import os
from pydantic_settings import BaseSettings
from pydantic import Field
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

_resolved_storage_dir = os.environ.get("STORAGE_DIR") or getDestinationFolder()
if _resolved_storage_dir:
    STORAGE_DIR = os.path.realpath(_resolved_storage_dir)
    TEMP_UPLOADS_DIR = os.path.join(STORAGE_DIR, "storagepod_tmp_upload")
else:
    STORAGE_DIR = None
    TEMP_UPLOADS_DIR = None

JSON_DIR = "/var/log/storagepod"
METRICS_FILE = os.path.join(JSON_DIR, "metrics.json")
HARDDISKS_INFO_FILE = os.path.join(JSON_DIR, "hard_disks_info.json")
SMART_INFO_FILE = os.path.join(JSON_DIR, "smart_info.json")
FILESYSTEM_INFO_FILE = os.path.join(JSON_DIR, "file_systems_info.json")
SYSTEMS_METRICS_FILE = os.path.join(JSON_DIR, "systems_metrics.json")
RECENT_ACTIVITY_FILE = os.path.join(JSON_DIR, "storagepod_recent_activity.json")

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost",
            "http://127.0.0.1",
            "https://localhost",
            "https://127.0.0.1",
            "http://storagepod.local",
            "https://storagepod.local",
        ]
    )
    # Use this if you want to allow subdomains without enumerating them, e.g.:
    # ^https?://.*\\.campuscatalyst\\.info$
    CORS_ALLOW_ORIGIN_REGEX: str | None = None
    # Bearer-token auth does not require credentials; keep this false unless you need cookies.
    CORS_ALLOW_CREDENTIALS: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
