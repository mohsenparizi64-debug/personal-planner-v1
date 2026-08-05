from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List

class SubGoalTaskBase(BaseModel):
    title: str
    is_completed: bool = False
    priority: int = 0
    due_date: Optional[date] = None

class SubGoalTaskCreate(SubGoalTaskBase):
    @field_validator("due_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

class SubGoalTaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[date] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

class SubGoalTaskRead(SubGoalTaskBase):
    id: int
    sub_goal_id: int
    owner_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class SubGoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: str = "not_started"
    progress_percent: int = 0
    order_index: int = 0

class SubGoalCreate(SubGoalBase):
    pass

class SubGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None
    order_index: Optional[int] = None

class SubGoalRead(SubGoalBase):
    id: int
    goal_id: int
    owner_id: int
    created_at: datetime
    tasks: List[SubGoalTaskRead] = []
    class Config:
        from_attributes = True