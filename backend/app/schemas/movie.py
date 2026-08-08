from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.pydantic_types import GDate

class MovieBase(BaseModel):
    title: str
    category: Optional[str] = None
    register_date: Optional[GDate] = None
    watch_date: Optional[GDate] = None
    rating: int = 0
    notes: Optional[str] = None
    is_watched: bool = False

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    register_date: Optional[GDate] = None
    watch_date: Optional[GDate] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_watched: Optional[bool] = None

class MovieRead(MovieBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True