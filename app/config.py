import os
from pathlib import Path

#here we need to find a logic to find the destination dir. "/srv/dev-disk-by-uuid-09698ee9-3b6f-4504-b43d-d7b527129ac9/Folder1"
STORAGE_DIR = os.environ.get("STORAGE_DIR", "/Users/pavan/Downloads/docs")


