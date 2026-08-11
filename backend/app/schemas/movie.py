from pydantic import BaseModel, ConfigDict
from typing import Optional, Union
from datetime import date

class MovieBase(BaseModel):
    title: str
    movie_type: Optional[str] = "movie"
    category: Optional[str] = None
    origin: Optional[str] = "foreign" # <--- اضافه شد
    register_date: Optional[Union[str, date]] = None
    watch_date: Optional[Union[str, date]] = None
    rating: Optional[int] = 0
    notes: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_url: Optional[str] = None
    is_watched: Optional[bool] = False

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    movie_type: Optional[str] = None
    category: Optional[str] = None
    origin: Optional[str] = None # <--- اضافه شد
    register_date: Optional[Union[str, date]] = None
    watch_date: Optional[Union[str, date]] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    poster_url: Optional[str] = None
    imdb_url: Optional[str] = None
    is_watched: Optional[bool] = None

class MovieRead(MovieBase):
    id: int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)