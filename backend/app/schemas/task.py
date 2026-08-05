from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    register_date: Optional[date] = None
    duration_days: Optional[int] = None
    #due_date: Optional[date] = None
    category: Optional[str] = None
    sub_goal_id: Optional[int] = None
    goal_id: Optional[int] = None
    last_action_date: Optional[date] = None
    status: str = "not_started"
    recurrence_type: Optional[str] = None
    recurrence_interval: int = 1
    recurrence_end_date: Optional[date] = None
    priority: int = 0

    @field_validator("register_date", "last_action_date", "recurrence_end_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    register_date: Optional[date] = None
    duration_days: Optional[int] = None
    due_date: Optional[date] = None
    category: Optional[str] = None
    sub_goal_id: Optional[int] = None
    goal_id: Optional[int] = None
    last_action_date: Optional[date] = None
    status: Optional[str] = None
    recurrence_type: Optional[str] = None
    recurrence_interval: Optional[int] = None
    recurrence_end_date: Optional[date] = None
    priority: Optional[int] = None
    is_completed: Optional[bool] = None

    @field_validator("register_date", "due_date", "last_action_date", "recurrence_end_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

class TaskRead(TaskBase):
    id: int
    is_completed: bool
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    days_until_due: Optional[int] = None
    days_until_recurrence: Optional[int] = None
    suggested_due_date: Optional[date] = None
    class Config:
        from_attributes = True