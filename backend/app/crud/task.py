from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.all_models import Task
from app.schemas.task import TaskCreate, TaskUpdate
from datetime import date, datetime, timedelta

def calculate_days_until_due(task):
    if not task.due_date:
        return None
    delta = task.due_date - date.today()
    return delta.days

def calculate_days_until_recurrence(task):
    if not task.recurrence_type or task.recurrence_type == 'none':
        return None
    if not task.last_action_date:
        return None
    today = date.today()
    last = task.last_action_date
    if task.recurrence_type == 'daily':
        next_date = last + timedelta(days=task.recurrence_interval)
    elif task.recurrence_type == 'weekly':
        next_date = last + timedelta(weeks=task.recurrence_interval)
    elif task.recurrence_type == 'monthly':
        next_date = last + timedelta(days=30 * task.recurrence_interval)
    elif task.recurrence_type == 'yearly':
        next_date = last + timedelta(days=365 * task.recurrence_interval)
    else:
        return None
    return (next_date - today).days

async def get_tasks(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Task)
        .where(Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.priority.desc(), Task.due_date.asc())
        .offset(skip)
        .limit(limit)
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
    db_task = Task(**task.model_dump(), owner_id=owner_id)
    if not db_task.register_date:
        db_task.register_date = date.today()
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
    if 'status' in update_data:
        db_task.last_action_date = date.today()
    for key, value in update_data.items():
        setattr(db_task, key, value)
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