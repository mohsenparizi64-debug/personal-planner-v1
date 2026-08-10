from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class SubGoalTaskBase(BaseModel):
    title: str
    is_completed: bool = False
    priority: int = 0
    due_date: Optional[str] = None
    description: Optional[str] = None 
    last_action_date: Optional[str] = None 
    category: Optional[str] = None
    duration_days: Optional[int] = None
    recurrence_type: Optional[str] = "none"
    recurrence_interval: Optional[int] = 1
    source: Optional[str] = "subgoal_task"

class SubGoalTaskCreate(SubGoalTaskBase):
    pass

class SubGoalTaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    last_action_date: Optional[str] = None
    category: Optional[str] = None

class SubGoalTaskRead(SubGoalTaskBase):
    id: int
    sub_goal_id: Optional[int] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class SubGoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    status: str = "not_started"
    progress_percent: int = 0
    order_index: int = 0

class SubGoalCreate(SubGoalBase):
    pass

class SubGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None

class SubGoalRead(SubGoalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    goal_id: int
    owner_id: int
    tasks: List[SubGoalTaskRead] = []