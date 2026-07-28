from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    category: Optional[str] = None
    register_date: Optional[date] = None
    read_date: Optional[date] = None
    rating: int = 0
    notes: Optional[str] = None
    is_read: bool = False

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    register_date: Optional[date] = None
    read_date: Optional[date] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    is_read: Optional[bool] = None

class BookRead(BookBase):
    id: int
    owner_id: int
    created_at: datetime
    class Config:
        from_attributes = True