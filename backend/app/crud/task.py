from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.all_models import Task
from app.schemas.task import TaskCreate, TaskUpdate
from datetime import date, datetime, timedelta

def calculate_suggested_due_date(task):
    """محاسبه تاریخ پیشنهادی"""
    if task.recurrence_type and task.recurrence_type != 'none' and task.last_action_date:
        if task.recurrence_type == 'daily':
            return task.last_action_date + timedelta(days=task.recurrence_interval)
        elif task.recurrence_type == 'weekly':
            return task.last_action_date + timedelta(weeks=task.recurrence_interval)
        elif task.recurrence_type == 'monthly':
            return task.last_action_date + timedelta(days=30 * task.recurrence_interval)
        elif task.recurrence_type == 'yearly':
            return task.last_action_date + timedelta(days=365 * task.recurrence_interval)
    elif task.duration_days and task.register_date:
        return task.register_date + timedelta(days=task.duration_days)
    elif task.due_date:
        return task.due_date
    return None

def calculate_days_until_due(task):
    due = task.due_date or calculate_suggested_due_date(task)
    if not due: return None
    return (due - date.today()).days

def calculate_days_until_recurrence(task):
    if not task.recurrence_type or task.recurrence_type == 'none': return None
    if not task.last_action_date: return None
    today = date.today()
    last = task.last_action_date
    if task.recurrence_type == 'daily': next_date = last + timedelta(days=task.recurrence_interval)
    elif task.recurrence_type == 'weekly': next_date = last + timedelta(weeks=task.recurrence_interval)
    elif task.recurrence_type == 'monthly': next_date = last + timedelta(days=30 * task.recurrence_interval)
    elif task.recurrence_type == 'yearly': next_date = last + timedelta(days=365 * task.recurrence_interval)
    else: return None
    return (next_date - today).days

async def get_tasks(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 50):
    result = await db.execute(
        select(Task).where(Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.priority.desc(), Task.due_date.asc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())

async def get_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
    )
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, task: TaskCreate, owner_id: int):
    from app.core.date_utils import shamsi_to_gregorian
    
    data = task.model_dump()
    
    # تبدیل تاریخ‌های شمسی به میلادی
    reg = await shamsi_to_gregorian(data.get('register_date'))
    data['register_date'] = reg if reg else date.today()
    
    last = await shamsi_to_gregorian(data.get('last_action_date'))
    data['last_action_date'] = last if last else date.today()
    
    rec = await shamsi_to_gregorian(data.get('recurrence_end_date'))
    data['recurrence_end_date'] = rec
    
    # حذف فیلدهای computed
    for key in ['due_date', 'suggested_due_date', 'days_until_due', 'days_until_recurrence']:
        data.pop(key, None)
    
    db_task = Task(**data, owner_id=owner_id)
    db_task.due_date = calculate_suggested_due_date(db_task)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update_task(db: AsyncSession, task_id: int, owner_id: int, task_update: TaskUpdate):
    from app.core.date_utils import shamsi_to_gregorian
    
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
    )
    db_task = result.scalar_one_or_none()
    if not db_task: return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    if 'register_date' in update_data:
        r = await shamsi_to_gregorian(update_data['register_date'])
        if r: update_data['register_date'] = r
    if 'last_action_date' in update_data:
        l = await shamsi_to_gregorian(update_data['last_action_date'])
        if l: update_data['last_action_date'] = l
    if 'recurrence_end_date' in update_data:
        e = await shamsi_to_gregorian(update_data['recurrence_end_date'])
        update_data['recurrence_end_date'] = e
    
    for key in ['due_date', 'suggested_due_date', 'days_until_due', 'days_until_recurrence']:
        update_data.pop(key, None)
    
    if 'status' in update_data: db_task.last_action_date = date.today()
    for key, value in update_data.items(): setattr(db_task, key, value)
    db_task.due_date = calculate_suggested_due_date(db_task)
    await db.commit(); await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    db_task = result.scalar_one_or_none()
    if not db_task: return None
    await db.delete(db_task); await db.commit()
    return db_task