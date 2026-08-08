from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.pydantic_types import GDate

class PlaceBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    register_date: Optional[GDate] = None
    is_visited: bool = False
    visit_date: Optional[GDate] = None
    rating: int = 0
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_favorite: bool = False

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    register_date: Optional[GDate] = None
    is_visited: Optional[bool] = None
    visit_date: Optional[GDate] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_favorite: Optional[bool] = None

class PlaceRead(PlaceBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True