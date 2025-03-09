from datetime import datetime
from typing import List, Generic, TypeVar
from pydantic import BaseModel, ConfigDict
from enum import Enum

T = TypeVar('T')

class EventType(str, Enum):
    """WebSocket event types for real-time updates"""
    TAG_DELETED = "tag_deleted"
    FAVORITE_UPDATED = "favorite_updated"
    NOTES_UPDATED = "notes_updated"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    SCREENSHOTS_DELETED = "screenshots_deleted"
    SETTINGS_UPDATED = "settings_updated"
    NEW_SCREENSHOT = "new_screenshot"

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ScreenshotResponse(BaseModel):
    id: int
    file_path: str
    timestamp: datetime
    app_name: str
    window_title: str
    extracted_text: str
    confidence_score: float
    is_favorite: bool
    notes: str | None = None
    summary: str | None = None
    tags: List[TagResponse]
    
    model_config = ConfigDict(from_attributes=True)

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
