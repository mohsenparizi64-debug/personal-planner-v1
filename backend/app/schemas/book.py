from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.pydantic_types import GDate

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    register_date: Optional[GDate] = None
    read_date: Optional[GDate] = None
    rating: int = 0
    notes: Optional[str] = None
    is_read: bool = False

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    register_date: Optional[GDate] = None
    read_date: Optional[GDate] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_read: Optional[bool] = None

class BookRead(BookBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True