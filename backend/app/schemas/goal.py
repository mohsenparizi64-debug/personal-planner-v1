from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.pydantic_types import GDate

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[GDate] = None
    target_date: Optional[GDate] = None
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
    start_date: Optional[GDate] = None
    target_date: Optional[GDate] = None
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

# اسکیما جهت رفع خطای ResponseValidationError در لاگ‌های تغییرات اهداف
class GoalLogRead(BaseModel):
    id: int
    goal_id: Optional[int] = None  # اختیاری بودن فیلد جهت جلوگیری از کرش هنگام NULL بودن
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True