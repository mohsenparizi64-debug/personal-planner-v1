from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import SubGoal, SubGoalTask, Task, KPI
from app.schemas.sub_goal import SubGoalCreate, SubGoalUpdate, SubGoalTaskCreate, SubGoalTaskUpdate
from app.schemas.kpi import KPICreate, KPIUpdate
from datetime import datetime

# --- تابع کلیدی: ادغام هوشمند و امن تسک‌ها از دو منبع ---
async def _attach_tasks(db: AsyncSession, sub_goal: SubGoal):
    # ۱. دریافت تسک‌های مستقیم (SubGoalTask)
    res1 = await db.execute(select(SubGoalTask).where(SubGoalTask.sub_goal_id == sub_goal.id))
    tasks1 = res1.scalars().all()
    
    # ۲. دریافت تسک‌های عمومی متصل شده (Task)
    res2 = await db.execute(select(Task).where(Task.sub_goal_id == sub_goal.id))
    tasks2 = res2.scalars().all()
    
    merged = []
    
    # پردازش تسک‌های جدول اختصاصی (با رعایت تمام فیلدها)
    for t in tasks1:
        merged.append({
            "id": t.id,
            "title": t.title,
            "is_completed": t.is_completed,
            "priority": t.priority or 0,
            "due_date": str(t.due_date) if t.due_date else None,
            "description": t.description,
            "last_action_date": str(t.last_action_date) if t.last_action_date else None,
            "category": getattr(t, 'category', None),
            "duration_days": getattr(t, 'duration_days', None),
            "source": "subgoal_task",
            "created_at": t.created_at or datetime.now() # حیاتی برای جلوگیری از رول‌بک
        })
        
    # پردازش تسک‌های جدول اصلی (با تبدیل امن اشیاء Date به String)
    for t in tasks2:
        merged.append({
            "id": t.id,
            "title": t.title,
            "is_completed": t.is_completed,
            "priority": t.priority or 0,
            "due_date": str(t.due_date) if t.due_date else None,
            "description": t.description,
            "last_action_date": str(t.last_action_date) if t.last_action_date else None,
            "category": t.category,
            "duration_days": t.duration_days,
            "source": "main_task",
            "created_at": t.created_at or datetime.now()
        })
    
    # مرتب‌سازی: انجام نشده‌ها اول، سپس بر اساس اهمیت
    merged.sort(key=lambda x: (x["is_completed"], -(x["priority"] or 0)))
    sub_goal.tasks = merged 
    return sub_goal

# --- مدیریت گام‌ها (SubGoals) ---

async def get_sub_goals(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(
        select(SubGoal).where(SubGoal.goal_id == goal_id, SubGoal.owner_id == owner_id).order_by(SubGoal.id)
    )
    sgs = result.scalars().all()
    for sg in sgs:
        await _attach_tasks(db, sg)
    return sgs

async def get_sub_goal_by_id(db: AsyncSession, sub_goal_id: int, owner_id: int):
    result = await db.execute(select(SubGoal).where(SubGoal.id == sub_goal_id, SubGoal.owner_id == owner_id))
    sg = result.scalar_one_or_none()
    if sg:
        await _attach_tasks(db, sg)
    return sg

async def create_sub_goal(db: AsyncSession, data: SubGoalCreate, goal_id: int, owner_id: int):
    db_sg = SubGoal(**data.model_dump(), goal_id=goal_id, owner_id=owner_id)
    db.add(db_sg); await db.commit(); await db.refresh(db_sg)
    return db_sg

async def update_sub_goal(db: AsyncSession, sub_goal_id: int, owner_id: int, update: SubGoalUpdate):
    res = await db.execute(select(SubGoal).where(SubGoal.id == sub_goal_id, SubGoal.owner_id == owner_id))
    db_sg = res.scalar_one_or_none()
    if db_sg:
        for k, v in update.model_dump(exclude_unset=True).items():
            setattr(db_sg, k, v)
        await db.commit(); await db.refresh(db_sg)
        return db_sg
    return None

async def delete_sub_goal(db: AsyncSession, id: int, owner_id: int):
    res = await db.execute(select(SubGoal).where(SubGoal.id == id, SubGoal.owner_id == owner_id))
    db_sg = res.scalar_one_or_none()
    if db_sg:
        await db.delete(db_sg); await db.commit()
        return True
    return False

# --- مدیریت تسک‌های گام (SubGoalTask) ---

async def create_sub_task(db: AsyncSession, data: SubGoalTaskCreate, sub_goal_id: int, owner_id: int):
    db_t = SubGoalTask(**data.model_dump(), sub_goal_id=sub_goal_id, owner_id=owner_id)
    db.add(db_t); await db.commit(); await db.refresh(db_t)
    return db_t

async def update_sub_task(db: AsyncSession, task_id: int, owner_id: int, update: SubGoalTaskUpdate):
    res = await db.execute(select(SubGoalTask).where(SubGoalTask.id == task_id, SubGoalTask.owner_id == owner_id))
    db_t = res.scalar_one_or_none()
    if db_t:
        for k, v in update.model_dump(exclude_unset=True).items():
            setattr(db_t, k, v)
        await db.commit(); await db.refresh(db_t)
        return db_t
    return None

async def delete_sub_task(db: AsyncSession, id: int, owner_id: int):
    res = await db.execute(select(SubGoalTask).where(SubGoalTask.id == id, SubGoalTask.owner_id == owner_id))
    db_t = res.scalar_one_or_none()
    if db_t:
        await db.delete(db_t); await db.commit()
        return True
    return False

# --- مدیریت شاخص‌ها (KPIs) ---

async def get_kpis(db: AsyncSession, goal_id: int, owner_id: int):
    res = await db.execute(select(KPI).where(KPI.goal_id == goal_id, KPI.owner_id == owner_id))
    return list(res.scalars().all())

async def create_kpi(db: AsyncSession, data: KPICreate, goal_id: int, owner_id: int):
    db_kpi = KPI(**data.model_dump(), goal_id=goal_id, owner_id=owner_id)
    db.add(db_kpi); await db.commit(); await db.refresh(db_kpi)
    return db_kpi

async def update_kpi(db: AsyncSession, id: int, owner_id: int, update: KPIUpdate):
    res = await db.execute(select(KPI).where(KPI.id == id, KPI.owner_id == owner_id))
    db_kpi = res.scalar_one_or_none()
    if db_kpi:
        for k, v in update.model_dump(exclude_unset=True).items():
            setattr(db_kpi, k, v)
        db_kpi.last_updated = datetime.now()
        await db.commit(); await db.refresh(db_kpi)
        return db_kpi
    return None

async def delete_kpi(db: AsyncSession, id: int, owner_id: int):
    res = await db.execute(select(KPI).where(KPI.id == id, KPI.owner_id == owner_id))
    db_kpi = res.scalar_one_or_none()
    if db_kpi:
        await db.delete(db_kpi); await db.commit()
        return True
    return False