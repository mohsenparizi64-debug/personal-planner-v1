from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

from app.core.pydantic_types import GDate

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    register_date: Optional[GDate] = None
    duration_days: Optional[int] = None
    category: Optional[str] = None
    sub_goal_id: Optional[int] = None
    goal_id: Optional[int] = None
    last_action_date: Optional[GDate] = None
    status: str = "not_started"
    recurrence_type: Optional[str] = None
    recurrence_interval: int = 1
    recurrence_end_date: Optional[GDate] = None
    priority: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    register_date: Optional[GDate] = None
    duration_days: Optional[int] = None
    due_date: Optional[GDate] = None
    category: Optional[str] = None
    sub_goal_id: Optional[int] = None
    goal_id: Optional[int] = None
    last_action_date: Optional[GDate] = None
    status: Optional[str] = None
    recurrence_type: Optional[str] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[GDate] = None
    priority: Optional[int] = None
    is_completed: Optional[bool] = None

class TaskRead(TaskBase):
    id: int
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    days_until_due: Optional[int] = None
    days_until_recurrence: Optional[int] = None
    suggested_due_date: Optional[GDate] = None

    class Config:
        from_attributes = True