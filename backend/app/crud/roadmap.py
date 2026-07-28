from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.all_models import SubGoal, SubGoalTask, KPI
from app.schemas.sub_goal import SubGoalCreate, SubGoalUpdate, SubGoalTaskCreate, SubGoalTaskUpdate
from app.schemas.kpi import KPICreate, KPIUpdate
from datetime import datetime

async def get_sub_goal_by_id(db: AsyncSession, sub_goal_id: int, owner_id: int):
    result = await db.execute(select(SubGoal).where(SubGoal.id == sub_goal_id, SubGoal.owner_id == owner_id).options(selectinload(SubGoal.tasks)))
    return result.scalar_one_or_none()

async def get_sub_goals(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(select(SubGoal).where(SubGoal.goal_id == goal_id, SubGoal.owner_id == owner_id).options(selectinload(SubGoal.tasks)).order_by(SubGoal.order_index))
    return list(result.scalars().all())

async def create_sub_goal(db: AsyncSession, sub_goal: SubGoalCreate, goal_id: int, owner_id: int):
    db_sub = SubGoal(**sub_goal.model_dump(), goal_id=goal_id, owner_id=owner_id)
    db.add(db_sub)
    await db.commit()
    await db.refresh(db_sub)
    return db_sub

async def update_sub_goal(db: AsyncSession, sub_goal_id: int, owner_id: int, update: SubGoalUpdate):
    result = await db.execute(select(SubGoal).where(SubGoal.id == sub_goal_id, SubGoal.owner_id == owner_id))
    db_sub = result.scalar_one_or_none()
    if not db_sub: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_sub, k, v)
    await db.commit(); await db.refresh(db_sub)
    return db_sub

async def delete_sub_goal(db: AsyncSession, sub_goal_id: int, owner_id: int):
    result = await db.execute(select(SubGoal).where(SubGoal.id == sub_goal_id, SubGoal.owner_id == owner_id))
    db_sub = result.scalar_one_or_none()
    if not db_sub: return None
    await db.delete(db_sub); await db.commit()
    return db_sub

async def create_sub_task(db: AsyncSession, task: SubGoalTaskCreate, sub_goal_id: int, owner_id: int):
    db_task = SubGoalTask(**task.model_dump(), sub_goal_id=sub_goal_id, owner_id=owner_id)
    db.add(db_task); await db.commit(); await db.refresh(db_task)
    return db_task

async def update_sub_task(db: AsyncSession, task_id: int, owner_id: int, update: SubGoalTaskUpdate):
    result = await db.execute(select(SubGoalTask).where(SubGoalTask.id == task_id, SubGoalTask.owner_id == owner_id))
    db_task = result.scalar_one_or_none()
    if not db_task: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_task, k, v)
    await db.commit(); await db.refresh(db_task)
    return db_task

async def delete_sub_task(db: AsyncSession, task_id: int, owner_id: int):
    result = await db.execute(select(SubGoalTask).where(SubGoalTask.id == task_id, SubGoalTask.owner_id == owner_id))
    db_task = result.scalar_one_or_none()
    if not db_task: return None
    await db.delete(db_task); await db.commit()
    return db_task

async def get_kpis(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(select(KPI).where(KPI.goal_id == goal_id, KPI.owner_id == owner_id))
    return list(result.scalars().all())

async def create_kpi(db: AsyncSession, kpi: KPICreate, goal_id: int, owner_id: int):
    db_kpi = KPI(**kpi.model_dump(), goal_id=goal_id, owner_id=owner_id)
    db.add(db_kpi); await db.commit(); await db.refresh(db_kpi)
    return db_kpi

async def update_kpi(db: AsyncSession, kpi_id: int, owner_id: int, update: KPIUpdate):
    result = await db.execute(select(KPI).where(KPI.id == kpi_id, KPI.owner_id == owner_id))
    db_kpi = result.scalar_one_or_none()
    if not db_kpi: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_kpi, k, v)
    db_kpi.last_updated = datetime.utcnow()
    await db.commit(); await db.refresh(db_kpi)
    return db_kpi

async def delete_kpi(db: AsyncSession, kpi_id: int, owner_id: int):
    result = await db.execute(select(KPI).where(KPI.id == kpi_id, KPI.owner_id == owner_id))
    db_kpi = result.scalar_one_or_none()
    if not db_kpi: return None
    await db.delete(db_kpi); await db.commit()
    return db_kpi