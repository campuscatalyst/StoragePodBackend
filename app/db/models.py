from sqlmodel import SQLModel, Field
from typing import Optional, Literal
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.now())

class FileEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    path: str = Field(index=True)
    type: Literal["file", "folder"] = Field(index=True)
    size: int
    modified_at: datetime
    created_at: datetime = Field(default_factory=datetime.now())
