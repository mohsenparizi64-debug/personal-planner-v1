from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import json
import re
from datetime import date

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.all_models import User
from app.schemas.bio_tracker import (
    UserBiometricsUpdate, UserBiometricsResponse,
    SpiritualTrackerCreate, SpiritualTrackerUpdate, SpiritualTrackerResponse, SpiritualLogCreate, SpiritualLogResponse,
    WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse, WorkoutEstimateRequest, WorkoutEstimateResponse,
    MealLogCreate, MealLogUpdate, MealLogResponse, MealEstimateRequest, MealEstimateResponse,
    HealthLogCreate, HealthLogResponse
)
from app.crud import bio_tracker as crud_bio

router = APIRouter()

@router.put("/biometrics", response_model=UserBiometricsResponse)
async def update_biometrics(
    data: UserBiometricsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud_bio.update_user_biometrics(db, current_user.id, data)

@router.post("/estimate-workout", response_model=WorkoutEstimateResponse)
async def estimate_workout_calories(
    req: WorkoutEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    user_weight = current_user.weight or 70.0
    user_target_weight = current_user.target_weight or user_weight
    user_height = current_user.height or 175.0
    user_gender = current_user.gender or "مرد"
    user_activity = current_user.activity_level or "متوسط"
    health_notes = current_user.health_notes or "بدون ملاحظه"
    
    user_age = "نامشخص"
    if current_user.birth_date:
        today = date.today()
        user_age = today.year - current_user.birth_date.year
        
    user_context = (
        f"وزن فعلی: {user_weight} کیلوگرم، وزن هدف: {user_target_weight} کیلوگرم، قد: {user_height} سانتی‌متر، "
        f"جنسیت: {user_gender}، سن: {user_age}، سطح فعالیت: {user_activity}، ملاحظات: {health_notes}"
    )
    
    prompt = f"""
    به عنوان یک مربی ورزشی و متخصص علوم فیتنس، کالری مصرفی دقیق این فعالیت بدنی را بر اساس مشخصات فیزیکی کاربر محاسبه کن:
    نوع ورزش: {req.workout_type}
    مدت زمان: {req.duration_minutes} دقیقه
    پروفایل فیزیکی کاربر: {user_context}
    
    پاسخ را **صرفاً و فقط** به فرمت JSON معتبر زیر ارائه بده:
    {{
        "estimated_calories": 280,
        "explanation": "توضیح کوتاه نحوه محاسبه بر اساس وزن، قد و نوع فعالیت"
    }}
    """
    
    avalai_url = "https://api.avalai.ir/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AVALAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                avalai_url,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )
            
            if response.status_code == 200:
                res_data = response.json()
                raw_content = res_data["choices"][0]["message"]["content"]
                json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    return WorkoutEstimateResponse(
                        estimated_calories=int(parsed_json.get("estimated_calories", 0)),
                        explanation=parsed_json.get("explanation", "محاسبه‌شده توسط AI مربی ورزشی")
                    )
            else:
                raise HTTPException(status_code=502, detail=f"⚠️ خطا در سرویس AI مربی ورزشی: {response.text}")
    except Exception as e:
        print(f"❌ AI Workout API Exception: {e}")
        raise HTTPException(status_code=502, detail=f"⚠️ عدم امکان ارتباط با AI مربی ورزشی: {str(e)}")

@router.post("/estimate-meal", response_model=MealEstimateResponse)
async def estimate_meal_nutrition(
    req: MealEstimateRequest,
    current_user: User = Depends(get_current_user)
):
    user_weight = current_user.weight or 70.0
    user_target_weight = current_user.target_weight or user_weight
    user_context = f"وزن فعلی: {user_weight} کیلوگرم، وزن هدف: {user_target_weight} کیلوگرم، جنسیت: {current_user.gender or 'نامشخص'}"
    
    prompt = f"""
    به عنوان AI کارشناس تغذیه و طب سنتی ایرانی، کالری و طبع دقیق این وعده غذایی را محاسبه کن:
    نام غذا: {req.food_name}
    مقدار و واحد: {req.portion_unit}
    وعده: {req.meal_type}
    پروفایل کاربر: {user_context}
    
    پاسخ را **صرفاً و فقط** به فرمت JSON معتبر زیر ارائه بده:
    {{
        "estimated_calories": 450,
        "temperament": "گرم و تر",
        "temperament_advice": "توصیه کوتاه مصلح غذایی"
    }}
    """
    
    avalai_url = "https://api.avalai.ir/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AVALAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                avalai_url,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )
            
            if response.status_code == 200:
                res_data = response.json()
                raw_content = res_data["choices"][0]["message"]["content"]
                json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                if json_match:
                    parsed_json = json.loads(json_match.group(0))
                    return MealEstimateResponse(
                        estimated_calories=int(parsed_json.get("estimated_calories", 0)),
                        temperament=parsed_json.get("temperament", "معتدل"),
                        temperament_advice=parsed_json.get("temperament_advice", "")
                    )
            else:
                raise HTTPException(status_code=502, detail=f"⚠️ خطا در سرویس AI کارشناس تغذیه: {response.text}")
    except Exception as e:
        print(f"❌ AI Meal API Exception: {e}")
        raise HTTPException(status_code=502, detail=f"⚠️ عدم امکان ارتباط با AI کارشناس تغذیه: {str(e)}")

# CRUD Endpoints
@router.get("/spiritual", response_model=list[SpiritualTrackerResponse])
async def list_spiritual(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.get_spiritual_trackers(db, current_user.id)

@router.post("/spiritual", response_model=SpiritualTrackerResponse)
async def create_spiritual(data: SpiritualTrackerCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.create_spiritual_tracker(db, current_user.id, data)

@router.put("/spiritual/{tracker_id}", response_model=SpiritualTrackerResponse)
async def update_spiritual(tracker_id: int, data: SpiritualTrackerUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await crud_bio.update_spiritual_tracker(db, current_user.id, tracker_id, data)
    if not t:
        raise HTTPException(status_code=404, detail="Spiritual tracker not found")
    return t

@router.delete("/spiritual/{tracker_id}")
async def delete_spiritual(tracker_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud_bio.delete_spiritual_tracker(db, current_user.id, tracker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spiritual tracker not found")
    return {"message": "Deleted successfully"}

@router.post("/spiritual/log", response_model=SpiritualLogResponse)
async def add_spiritual_log(data: SpiritualLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.add_spiritual_log(db, current_user.id, data)

@router.get("/workout", response_model=list[WorkoutLogResponse])
async def list_workouts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.get_workout_logs(db, current_user.id)

@router.post("/workout", response_model=WorkoutLogResponse)
async def create_workout(data: WorkoutLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.create_workout_log(db, current_user.id, data)

@router.put("/workout/{workout_id}", response_model=WorkoutLogResponse)
async def update_workout(workout_id: int, data: WorkoutLogUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    w = await crud_bio.update_workout_log(db, current_user.id, workout_id, data)
    if not w:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return w

@router.delete("/workout/{workout_id}")
async def delete_workout(workout_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud_bio.delete_workout_log(db, current_user.id, workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout log not found")
    return {"message": "Deleted successfully"}

@router.get("/meal", response_model=list[MealLogResponse])
async def list_meals(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.get_meal_logs(db, current_user.id)

@router.post("/meal", response_model=MealLogResponse)
async def create_meal(data: MealLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.create_meal_log(db, current_user.id, data)

@router.put("/meal/{meal_id}", response_model=MealLogResponse)
async def update_meal(meal_id: int, data: MealLogUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    m = await crud_bio.update_meal_log(db, current_user.id, meal_id, data)
    if not m:
        raise HTTPException(status_code=404, detail="Meal log not found")
    return m

@router.delete("/meal/{meal_id}")
async def delete_meal(meal_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await crud_bio.delete_meal_log(db, current_user.id, meal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal log not found")
    return {"message": "Deleted successfully"}

@router.get("/health", response_model=list[HealthLogResponse])
async def list_health(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.get_health_logs(db, current_user.id)

@router.post("/health", response_model=HealthLogResponse)
async def create_health(data: HealthLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_bio.create_health_log(db, current_user.id, data)