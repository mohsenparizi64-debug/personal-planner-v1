from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    current_status: Optional[str] = None
    current_obstacle: Optional[str] = None
    next_step: Optional[str] = None
    priority: int = 0
    success_criteria: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    current_status: Optional[str] = None
    current_obstacle: Optional[str] = None
    next_step: Optional[str] = None
    priority: Optional[int] = None
    success_criteria: Optional[str] = None
    is_completed: Optional[bool] = None
    progress_percent: Optional[int] = None

class GoalRead(GoalBase):
    id: int
    is_completed: bool
    progress_percent: int
    owner_id: int
    created_at: datetime
    class Config:
        from_attributes = True