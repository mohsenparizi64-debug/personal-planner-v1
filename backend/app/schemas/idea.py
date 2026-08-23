from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, date

class IdeaBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = "عمومی"
    status: Optional[str] = "raw"
    excitement_rating: Optional[int] = 3
    reference_links: Optional[str] = None
    tags: Optional[str] = None
    is_archived: Optional[bool] = False
    goal_id: Optional[int] = None
    sub_goal_id: Optional[int] = None              # لینک به گام عملیاتی (SubGoal)

class IdeaCreate(IdeaBase):
    pass

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    excitement_rating: Optional[int] = None
    reference_links: Optional[str] = None
    tags: Optional[str] = None
    is_archived: Optional[bool] = None
    goal_id: Optional[int] = None
    sub_goal_id: Optional[int] = None

class IdeaRead(IdeaBase):
    id: int
    owner_id: int
    converted_to_goal_id: Optional[int] = None
    converted_to_task_id: Optional[int] = None
    conversion_date: Optional[date] = None           # تاریخ تبدیل ایده
    live_status_info: Optional[Dict[str, Any]] = None  # اطلاعات وضعیت زنده هدف/تسک
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)