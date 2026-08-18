from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime

class UserBiometricsUpdate(BaseModel):
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    target_weight: Optional[float] = None
    activity_level: Optional[str] = None
    health_notes: Optional[str] = None
    ai_persona_tone: Optional[str] = "friendly_expert"

class UserBiometricsResponse(UserBiometricsUpdate):
    id: int
    full_name: Optional[str] = None
    email: str
    
    model_config = ConfigDict(from_attributes=True)

class SpiritualLogBase(BaseModel):
    log_date: date
    log_time: Optional[str] = None
    count_change: int = 1
    notes: Optional[str] = None

class SpiritualLogCreate(SpiritualLogBase):
    tracker_id: int

class SpiritualLogResponse(SpiritualLogBase):
    id: int
    tracker_id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class SpiritualTrackerBase(BaseModel):
    title: str
    tracker_type: str = "prayer_qada"
    total_needed: int = 0
    completed_count: int = 0
    unit: str = "روز"
    register_date: Optional[date] = None
    last_action_date: Optional[date] = None
    notes: Optional[str] = None

class SpiritualTrackerCreate(SpiritualTrackerBase):
    pass

class SpiritualTrackerUpdate(BaseModel):
    title: Optional[str] = None
    total_needed: Optional[int] = None
    completed_count: Optional[int] = None
    unit: Optional[str] = None
    register_date: Optional[date] = None
    last_action_date: Optional[date] = None
    notes: Optional[str] = None

class SpiritualTrackerResponse(SpiritualTrackerBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    logs: List[SpiritualLogResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class HealthLogBase(BaseModel):
    log_date: date
    weight: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None

class HealthLogCreate(HealthLogBase):
    pass

class HealthLogResponse(HealthLogBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class WorkoutLogBase(BaseModel):
    log_date: date
    log_time: Optional[str] = None
    workout_type: str
    duration_minutes: int
    calories_burned: int = 0
    notes: Optional[str] = None

class WorkoutLogCreate(WorkoutLogBase):
    pass

class WorkoutLogUpdate(BaseModel):
    log_date: Optional[date] = None
    log_time: Optional[str] = None
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None

class WorkoutLogResponse(WorkoutLogBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class WorkoutEstimateRequest(BaseModel):
    workout_type: str
    duration_minutes: int

class WorkoutEstimateResponse(BaseModel):
    estimated_calories: int
    explanation: Optional[str] = None

class MealLogBase(BaseModel):
    log_date: date
    log_time: Optional[str] = None
    meal_type: str
    food_name: str
    portion_unit: str
    calories: int = 0
    temperament: Optional[str] = None
    notes: Optional[str] = None

class MealLogCreate(MealLogBase):
    pass

class MealLogUpdate(BaseModel):
    log_date: Optional[date] = None
    log_time: Optional[str] = None
    meal_type: Optional[str] = None
    food_name: Optional[str] = None
    portion_unit: Optional[str] = None
    calories: Optional[int] = None
    temperament: Optional[str] = None
    notes: Optional[str] = None

class MealLogResponse(MealLogBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class MealEstimateRequest(BaseModel):
    food_name: str
    portion_unit: str
    meal_type: Optional[str] = "ناهار"

class MealEstimateResponse(BaseModel):
    estimated_calories: int
    temperament: str
    temperament_advice: Optional[str] = None

class HabitLogBase(BaseModel):
    log_date: date
    is_completed: bool = True
    notes: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    habit_id: int

class HabitLogResponse(HabitLogBase):
    id: int
    habit_id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)

class HabitBase(BaseModel):
    title: str
    category: str = "سلامتی"
    frequency: str = "daily"
    target_days_per_week: int = 7
    is_active: bool = True

class HabitCreate(HabitBase):
    pass

class HabitResponse(HabitBase):
    id: int
    owner_id: int
    logs: List[HabitLogResponse] = []
    
    model_config = ConfigDict(from_attributes=True)