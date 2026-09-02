from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime

class LearningLogBase(BaseModel):
    title: str
    content: Optional[str] = None
    log_date: date
    resource_url: Optional[str] = None
    tags: Optional[str] = None
    skill_id: Optional[int] = None
    duration_minutes: Optional[int] = None  # مدت زمان یادگیری (برای streak)

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
    goal_id: Optional[int] = None      # null = مهارت مستقل (بدون هدف)
    notes: Optional[str] = None
    # فیلدهای جدید
    start_date: Optional[date] = None
    last_practiced: Optional[date] = None
    level: Optional[str] = "beginner"   # beginner, intermediate, advanced
    source_url: Optional[str] = None
    target_hours: Optional[int] = None
    practiced_hours: Optional[float] = 0

    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        if v not in ('beginner', 'intermediate', 'advanced'):
            return 'beginner'
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ('in_progress', 'mastered', 'on_hold'):
            return 'in_progress'
        return v

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    progress_percent: Optional[int] = None
    goal_id: Optional[int] = None
    notes: Optional[str] = None
    start_date: Optional[date] = None
    last_practiced: Optional[date] = None
    level: Optional[str] = None
    source_url: Optional[str] = None
    target_hours: Optional[int] = None
    practiced_hours: Optional[float] = None

class SkillResponse(SkillBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    learning_logs: List[LearningLogResponse] = []
    goal_title: Optional[str] = None  # برای نمایش در frontend

    model_config = ConfigDict(from_attributes=True)


# Schema برای stats
class SkillStats(BaseModel):
    total_skills: int = 0
    mastered: int = 0
    in_progress: int = 0
    on_hold: int = 0
    independent_skills: int = 0  # بدون هدف
    overall_progress_avg: float = 0  # میانگین پیشرفت
    current_streak: int = 0  # روزهای متوالی
    longest_streak: int = 0
    total_practiced_hours: float = 0
    by_category: dict = {}  # دسته‌بندی: تعداد
    recent_activity_30days: int = 0  # تعداد یادگیری در ۳۰ روز اخیر