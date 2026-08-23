from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime

class LearningLogBase(BaseModel):
    title: str
    content: Optional[str] = None
    log_date: date
    resource_url: Optional[str] = None
    tags: Optional[str] = None
    skill_id: Optional[int] = None

class LearningLogCreate(LearningLogBase):
    pass

class LearningLogResponse(LearningLogBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class SkillBase(BaseModel):
    title: str
    category: Optional[str] = "عمومی"
    status: str = "in_progress"         # in_progress, mastered, on_hold
    progress_percent: int = 0           # 0 to 100
    goal_id: Optional[int] = None      # لینک به هدف کلان استراتژیک
    notes: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None
    goal_id: Optional[int] = None
    notes: Optional[str] = None

class SkillResponse(SkillBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    learning_logs: List[LearningLogResponse] = []
    
    model_config = ConfigDict(from_attributes=True)