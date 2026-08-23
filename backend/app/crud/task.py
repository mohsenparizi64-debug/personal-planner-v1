from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from datetime import date, timedelta
from typing import Optional

from app.models.all_models import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.date_utils import add_months

def calculate_next_recurrence(task) -> Optional[date]:
    """تاریخ بعدی بر اساس تکرار با ماه واقعی."""
    if not task.recurrence_type or task.recurrence_type == "none":
        return None
    last = task.last_action_date or date.today()
    interval = task.recurrence_interval or 1
    
    if task.recurrence_type == "daily":
        next_d = last + timedelta(days=interval)
    elif task.recurrence_type == "weekly":
        next_d = last + timedelta(weeks=interval)
    elif task.recurrence_type == "monthly":
        next_d = add_months(last, interval)
    elif task.recurrence_type == "yearly":
        next_d = add_months(last, interval * 12)
    else:
        return None

    # بررسی تاریخ پایان تکرار (در صورت غیرفعال بودن مداومت تکرار)
    if hasattr(task, 'is_infinite_recurrence') and not task.is_infinite_recurrence:
        if task.recurrence_end_date and next_d > task.recurrence_end_date:
            return None

    return next_d

def calculate_suggested_due_date(task) -> Optional[date]:
    if task.duration_days and task.register_date:
        return task.register_date + timedelta(days=task.duration_days)
    rec = calculate_next_recurrence(task)
    if rec:
        return rec
    if task.due_date:
        return task.due_date
    if task.last_action_date:
        return task.last_action_date
    return None

def calculate_days_until(due: Optional[date]) -> Optional[int]:
    return (due - date.today()).days if due else None

def calculate_days_until_due(task) -> Optional[int]:
    rec = calculate_next_recurrence(task)
    days = calculate_days_until(rec)
    if days is not None:
        return days
    suggested = calculate_suggested_due_date(task)
    return calculate_days_until(suggested)

def calculate_days_until_recurrence(task) -> Optional[int]:
    rec = calculate_next_recurrence(task)
    return calculate_days_until(rec)

# دریافت تسک‌ها با بررسی اتوماتیک چرخه حیات موعد بعدی تسک‌های دوره‌ای
async def get_tasks(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 5000):
    result = await db.execute(
        select(Task)
        .where(Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.priority.desc(), Task.due_date.asc())
        .limit(limit)
        .offset(skip)
    )
    all_t = list(result.scalars().all())
    today = date.today()

    # موتور انتقال هوشمند: اگر موعد بعدی رسید، وضعیت به در انتظار اقدام (not_started) برمی‌گردد
    for t in all_t:
        has_rec = t.recurrence_type and t.recurrence_type != "none"
        if has_rec and t.is_completed and t.due_date and t.due_date <= today and t.last_action_date and t.last_action_date < today:
            t.is_completed = False
            t.status = "not_started"

    return all_t

async def get_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
    )
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, task: TaskCreate, owner_id: int):
    data = task.model_dump()
    data["register_date"] = data.get("register_date") or date.today()
    data["last_action_date"] = data.get("last_action_date") or date.today()
    data["status"] = data.get("status") or "not_started"

    db_task = Task(**data, owner_id=owner_id)
    if not db_task.due_date:
        db_task.due_date = calculate_suggested_due_date(db_task)

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update_task(db: AsyncSession, task_id: int, owner_id: int, task_update: TaskUpdate):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    is_marking_completed = update_data.get("is_completed") is True or update_data.get("status") == "completed"

    if update_data.get("status") is not None or is_marking_completed or not db_task.last_action_date:
        db_task.last_action_date = date.today()

    for key, value in update_data.items():
        setattr(db_task, key, value)

    if not db_task.due_date:
        db_task.due_date = calculate_suggested_due_date(db_task)

    # منطق تیک زدن: ثبت وضعیت completed و زمان‌بندی موعد بعدی
    if is_marking_completed:
        db_task.is_completed = True
        db_task.status = "completed"

        has_recurrence = db_task.recurrence_type and db_task.recurrence_type != "none"
        if has_recurrence:
            next_due = calculate_next_recurrence(db_task)
            if next_due:
                db_task.due_date = next_due
                # تسک برای امروز به عنوان تکمیل‌شده باقی می‌ماند تا زمانی که به تاریخ next_due برسد

    await db.commit()
    await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    )
    db_task = result.scalar_one_or_none()
    if not db_task:
        return None
    await db.delete(db_task)
    await db.commit()
    return db_task