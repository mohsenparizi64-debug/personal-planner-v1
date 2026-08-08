from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from app.core.pydantic_types import GDate

class SubGoalTaskBase(BaseModel):
    title: str
    is_completed: bool = False
    priority: int = 0
    due_date: Optional[GDate] = None

class SubGoalTaskCreate(SubGoalTaskBase):
    pass

class SubGoalTaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[GDate] = None

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
    start_date: Optional[GDate] = None
    target_date: Optional[GDate] = None
    status: str = "not_started"
    progress_percent: int = 0
    order_index: int = 0

class SubGoalCreate(SubGoalBase):
    pass

class SubGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[GDate] = None
    target_date: Optional[GDate] = None
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