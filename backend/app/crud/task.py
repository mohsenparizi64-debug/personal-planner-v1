from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    if not task.last_action_date:
        return None
    last = task.last_action_date
    interval = task.recurrence_interval or 1
    if task.recurrence_type == "daily":
        return last + timedelta(days=interval)
    if task.recurrence_type == "weekly":
        return last + timedelta(weeks=interval)
    if task.recurrence_type == "monthly":
        return add_months(last, interval)
    if task.recurrence_type == "yearly":
        return add_months(last, interval * 12)
    return None


def calculate_suggested_due_date(task) -> Optional[date]:
    """اولویت: تکرار -> مدت -> due_date کاربر -> آخرین اقدام."""
    rec = calculate_next_recurrence(task)
    if rec:
        return rec
    if task.duration_days and task.register_date:
        return task.register_date + timedelta(days=task.duration_days)
    if task.due_date:
        return task.due_date
    if task.last_action_date:
        return task.last_action_date
    return None


def calculate_days_until(due: Optional[date]) -> Optional[int]:
    return (due - date.today()).days if due else None

def calculate_days_until_due(task) -> Optional[int]:
    """موجودی برای سازگاری با API قدیمی."""
    rec = calculate_next_recurrence(task)
    days = calculate_days_until(rec)
    if days is not None:
        return days

    suggested = calculate_suggested_due_date(task)
    return calculate_days_until(suggested)


def calculate_days_until_recurrence(task) -> Optional[int]:
    """موجودی برای سازگاری با API قدیمی."""
    rec = calculate_next_recurrence(task)
    return calculate_days_until(rec)

async def get_tasks(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Task)
        .where(Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.priority.desc(), Task.due_date.asc())
        .limit(limit)
        .offset(skip)
    )
    return list(result.scalars().all())


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

    db_task = Task(**data, owner_id=owner_id)
    db_task.due_date = (
        db_task.due_date
        if db_task.due_date
        else calculate_suggested_due_date(db_task)
    )
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

    if update_data.get("status") is not None:
        db_task.last_action_date = date.today()

    for key, value in update_data.items():
        setattr(db_task, key, value)

    if "due_date" not in update_data:
        db_task.due_date = calculate_suggested_due_date(db_task)

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