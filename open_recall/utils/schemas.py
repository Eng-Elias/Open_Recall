from datetime import datetime
from typing import List, Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

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
