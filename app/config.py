import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

#here we need to find a logic to find the destination dir. "/srv/dev-disk-by-uuid-09698ee9-3b6f-4504-b43d-d7b527129ac9/Folder1"
#/Users/pavan/Downloads/docs
STORAGE_DIR = os.environ.get("STORAGE_DIR", "/Users/pavan/Downloads/docs")

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()

