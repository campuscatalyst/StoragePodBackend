from sqlmodel import SQLModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    file = "file"
    folder = "folder"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UploadTask(SQLModel, table=True):
    task_id: str = Field(primary_key=True, index=True)
    filename: str = Field(index=True)
    status: str = Field(default="uploading", index=True)   # uploading, done, failed
    written: int = Field(default=0)
    total: int = Field(default=0)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class FileEntry(SQLModel, table=True):
    file_id: str = Field(primary_key=True)
    name: str = Field(index=True)
    path: str = Field(index=True, unique=True)
    type: FileType = Field(index=True)
    size: int
    modified_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)

# ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name,bit_rate,r_frame_rate,duration -of json input.mp4

class MediaEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    path: str # Full file path 
    folder_path: str # Parent folder path
    type: str  # 'image' or 'video'
    size: Optional[int] = 0
    width: Optional[float]
    height: Optional[float]
    modified_at: datetime

    # Shared metadata
    mimetype: Optional[str] = None
    thumbnail: Optional[str] = None   # Path to thumbnail file (pre-generated)

    # Video-specific
    duration: Optional[float] = None     # seconds
    resolution: Optional[str] = None     # '1920x1080'
    codec: Optional[str] = None          # e.g. 'H.264'
    bitrate: Optional[int] = None        # kbps
    framerate: Optional[float] = None    # fps
