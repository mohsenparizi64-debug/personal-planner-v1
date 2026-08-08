from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KPIBase(BaseModel):
    title: str
    unit: str
    target_value: float = 0
    current_value: float = 0
    frequency: str = "monthly"

class KPICreate(KPIBase):
    pass

class KPIUpdate(BaseModel):
    title: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    frequency: Optional[str] = None

class KPIRead(KPIBase):
    id: int
    goal_id: int
    owner_id: int
    last_updated: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True