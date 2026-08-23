from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GoalLogRead(BaseModel):
    id: int
    goal_id: int
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True