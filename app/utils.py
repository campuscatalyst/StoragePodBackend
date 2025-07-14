import os
import mimetypes
from app.db.main import get_session
from app.logger import logger
from app.db.models import FileEntry, MediaEntry
import datetime

def is_media_file(path: str) -> str | None:
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        return None
    if mime_type.startswith("image"):
        return "image"
    elif mime_type.startswith("video"):
        return "video"
    return None

def is_first_boot():
    return not os.path.exists("first_boot.lock")

def mark_first_boot_done():
    with open("first_boot.lock", "w") as f:
        f.write("initialized")

def scan_and_insert(root_path: str):
    """
        NOTE - Make sure that this function isn't executed unnecessarily as this may consume lot of resources and time to iterate everything and add to the db. 
    """
    try:
        session = get_session()
        for dirpath, dirnames, filenames in os.walk(root_path):
            for dirname in dirnames:
                full_path = os.path.join(dirpath, dirname)
                rel_path = os.path.relpath(full_path, root_path)

                stat = os.stat(full_path)

                entry = FileEntry(
                    path=rel_path,
                    name=dirname,
                    type="folder",
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime)
                )

                session.merge(entry)

            for name in filenames:
                full_path = os.path.join(dirpath, name)
                rel_path = os.path.relpath(full_path, root_path)

                stat = os.stat(full_path)

                entry = FileEntry(
                    path=rel_path,
                    name=name,
                    type="file",
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime)
                )

                session.merge(entry)

        # once all the changes are added, then we will commit this. 
        session.commit()
    except Exception as e:
        logger.error(f"Error while scanning the folder to insert into db - {e}")
