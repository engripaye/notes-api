from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: Optional[str] = None
    filename: Optional[str] = None
    stored_filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
