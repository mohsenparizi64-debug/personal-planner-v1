from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from datetime import date
from app.models.all_models import (
    User, SpiritualTracker, SpiritualLog, HealthLog, 
    WorkoutLog, MealLog, Habit, HabitLog
)
from app.schemas.bio_tracker import (
    UserBiometricsUpdate, SpiritualTrackerCreate, SpiritualTrackerUpdate, SpiritualLogCreate,
    HealthLogCreate, WorkoutLogCreate, WorkoutLogUpdate, MealLogCreate, MealLogUpdate, HabitCreate, HabitLogCreate
)

async def update_user_biometrics(db: AsyncSession, user_id: int, data: UserBiometricsUpdate) -> User:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        update_dict = data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(user, key, val)
        await db.commit()
        await db.refresh(user)
    return user

async def get_spiritual_trackers(db: AsyncSession, user_id: int, limit: int = 5000):
    query = (
        select(SpiritualTracker)
        .options(selectinload(SpiritualTracker.logs))
        .where(SpiritualTracker.owner_id == user_id)
        .order_by(desc(SpiritualTracker.id))
        .limit(limit)
    )
    res = await db.execute(query)
    return res.scalars().all()

# ساخت هدف معنوی با لود صریح selectinload جهت رفع قطعی MissingGreenlet
async def create_spiritual_tracker(db: AsyncSession, user_id: int, data: SpiritualTrackerCreate):
    tracker_dict = data.model_dump()
    if not tracker_dict.get("register_date"):
        tracker_dict["register_date"] = date.today()
    if not tracker_dict.get("last_action_date"):
        tracker_dict["last_action_date"] = tracker_dict["register_date"]
        
    tracker = SpiritualTracker(**tracker_dict, owner_id=user_id)
    db.add(tracker)
    await db.commit()
    
    # خواندن مجدد مدل به همراه ریلیشن‌ها جهت جلوگیری از MissingGreenlet
    query = (
        select(SpiritualTracker)
        .options(selectinload(SpiritualTracker.logs))
        .where(SpiritualTracker.id == tracker.id)
    )
    res = await db.execute(query)
    return res.scalar_one()

# ویرایش هدف معنوی با لود صریح selectinload
async def update_spiritual_tracker(db: AsyncSession, user_id: int, tracker_id: int, data: SpiritualTrackerUpdate):
    q = select(SpiritualTracker).where(SpiritualTracker.id == tracker_id, SpiritualTracker.owner_id == user_id)
    res = await db.execute(q)
    tracker = res.scalar_one_or_none()
    if tracker:
        update_data = data.model_dump(exclude_unset=True)
        if "last_action_date" not in update_data or not update_data["last_action_date"]:
            update_data["last_action_date"] = date.today()
            
        for k, v in update_data.items():
            setattr(tracker, k, v)
        await db.commit()
        
        query = (
            select(SpiritualTracker)
            .options(selectinload(SpiritualTracker.logs))
            .where(SpiritualTracker.id == tracker_id)
        )
        res_up = await db.execute(query)
        return res_up.scalar_one()
    return None

async def delete_spiritual_tracker(db: AsyncSession, user_id: int, tracker_id: int):
    q = select(SpiritualTracker).where(SpiritualTracker.id == tracker_id, SpiritualTracker.owner_id == user_id)
    res = await db.execute(q)
    tracker = res.scalar_one_or_none()
    if tracker:
        await db.delete(tracker)
        await db.commit()
        return True
    return False

async def add_spiritual_log(db: AsyncSession, user_id: int, data: SpiritualLogCreate):
    log = SpiritualLog(**data.model_dump(), owner_id=user_id)
    db.add(log)
    
    q = select(SpiritualTracker).where(SpiritualTracker.id == data.tracker_id, SpiritualTracker.owner_id == user_id)
    res = await db.execute(q)
    tracker = res.scalar_one_or_none()
    if tracker:
        tracker.completed_count += data.count_change
        tracker.last_action_date = date.today()
        
    await db.commit()
    await db.refresh(log)
    return log

async def get_workout_logs(db: AsyncSession, user_id: int, limit: int = 5000):
    q = select(WorkoutLog).where(WorkoutLog.owner_id == user_id).order_by(desc(WorkoutLog.log_date), desc(WorkoutLog.id)).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

async def create_workout_log(db: AsyncSession, user_id: int, data: WorkoutLogCreate):
    workout = WorkoutLog(**data.model_dump(), owner_id=user_id)
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout

async def update_workout_log(db: AsyncSession, user_id: int, workout_id: int, data: WorkoutLogUpdate):
    q = select(WorkoutLog).where(WorkoutLog.id == workout_id, WorkoutLog.owner_id == user_id)
    res = await db.execute(q)
    w = res.scalar_one_or_none()
    if w:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(w, k, v)
        await db.commit()
        await db.refresh(w)
    return w

async def delete_workout_log(db: AsyncSession, user_id: int, workout_id: int):
    q = select(WorkoutLog).where(WorkoutLog.id == workout_id, WorkoutLog.owner_id == user_id)
    res = await db.execute(q)
    w = res.scalar_one_or_none()
    if w:
        await db.delete(w)
        await db.commit()
        return True
    return False

async def get_meal_logs(db: AsyncSession, user_id: int, limit: int = 5000):
    q = select(MealLog).where(MealLog.owner_id == user_id).order_by(desc(MealLog.log_date), desc(MealLog.id)).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

async def create_meal_log(db: AsyncSession, user_id: int, data: MealLogCreate):
    meal = MealLog(**data.model_dump(), owner_id=user_id)
    db.add(meal)
    await db.commit()
    await db.refresh(meal)
    return meal

async def update_meal_log(db: AsyncSession, user_id: int, meal_id: int, data: MealLogUpdate):
    q = select(MealLog).where(MealLog.id == meal_id, MealLog.owner_id == user_id)
    res = await db.execute(q)
    m = res.scalar_one_or_none()
    if m:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(m, k, v)
        await db.commit()
        await db.refresh(m)
    return m

async def delete_meal_log(db: AsyncSession, user_id: int, meal_id: int):
    q = select(MealLog).where(MealLog.id == meal_id, MealLog.owner_id == user_id)
    res = await db.execute(q)
    m = res.scalar_one_or_none()
    if m:
        await db.delete(m)
        await db.commit()
        return True
    return False

async def get_health_logs(db: AsyncSession, user_id: int, limit: int = 5000):
    q = select(HealthLog).where(HealthLog.owner_id == user_id).order_by(desc(HealthLog.log_date)).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

async def create_health_log(db: AsyncSession, user_id: int, data: HealthLogCreate):
    q = (
        select(HealthLog)
        .where(HealthLog.owner_id == user_id, HealthLog.log_date == data.log_date)
        .order_by(desc(HealthLog.id))
    )
    res = await db.execute(q)
    existing_h = res.scalars().first()
    
    if existing_h:
        if data.weight: existing_h.weight = data.weight
        if data.height: existing_h.height = data.height
        h = existing_h
    else:
        h = HealthLog(**data.model_dump(), owner_id=user_id)
        db.add(h)
    
    q_u = select(User).where(User.id == user_id)
    res_u = await db.execute(q_u)
    user = res_u.scalar_one_or_none()
    if user:
        if data.weight: user.weight = data.weight
        if data.height: user.height = data.height
            
    await db.commit()
    await db.refresh(h)
    return h