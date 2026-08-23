from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

from app.schemas.sub_goal import SubGoalRead

class PhaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0
    status: str = "not_started"
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    progress_percent: int = 0
    color: Optional[str] = None

class PhaseCreate(PhaseBase):
    pass

class PhaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    progress_percent: Optional[int] = None
    color: Optional[str] = None

class PhaseRead(PhaseBase):
    id: int
    goal_id: int
    owner_id: int
    created_at: datetime
    sub_goals: List[SubGoalRead] = []
    class Config:
        from_attributes = True