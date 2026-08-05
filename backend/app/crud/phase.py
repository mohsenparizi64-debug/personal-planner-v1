from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.all_models import Phase, SubGoal
from app.schemas.phase import PhaseCreate, PhaseUpdate

async def get_phases(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(
        select(Phase)
        .where(Phase.goal_id == goal_id, Phase.owner_id == owner_id)
        .options(selectinload(Phase.sub_goals).selectinload(SubGoal.tasks))
        .order_by(Phase.order_index)
    )
    return list(result.scalars().all())

async def get_phase(db: AsyncSession, phase_id: int, owner_id: int):
    result = await db.execute(
        select(Phase)
        .where(Phase.id == phase_id, Phase.owner_id == owner_id)
        .options(selectinload(Phase.sub_goals).selectinload(SubGoal.tasks))
    )
    return result.scalar_one_or_none()

async def create_phase(db: AsyncSession, phase: PhaseCreate, goal_id: int, owner_id: int):
    db_phase = Phase(**phase.model_dump(), goal_id=goal_id, owner_id=owner_id)
    db.add(db_phase)
    await db.commit()
    await db.refresh(db_phase)
    return db_phase

async def update_phase(db: AsyncSession, phase_id: int, owner_id: int, update: PhaseUpdate):
    result = await db.execute(
        select(Phase).where(Phase.id == phase_id, Phase.owner_id == owner_id)
    )
    db_phase = result.scalar_one_or_none()
    if not db_phase:
        return None
    for k, v in update.model_dump(exclude_unset=True).items():
        setattr(db_phase, k, v)
    await db.commit()
    await db.refresh(db_phase)
    return db_phase

async def delete_phase(db: AsyncSession, phase_id: int, owner_id: int):
    result = await db.execute(
        select(Phase).where(Phase.id == phase_id, Phase.owner_id == owner_id)
    )
    db_phase = result.scalar_one_or_none()
    if not db_phase:
        return None
    await db.delete(db_phase)
    await db.commit()
    return db_phase