"""Announcement (classroom stream post) request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    content: str


class AnnouncementOut(BaseModel):
    id: str
    classroom_id: str
    author_id: str
    author_name: Optional[str] = None
    content: str
    created_at: datetime
