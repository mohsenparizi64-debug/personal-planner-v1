from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.phase import PhaseCreate, PhaseUpdate, PhaseRead
from app.crud import phase as phase_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/goal/{goal_id}/phases", response_model=List[PhaseRead])
async def get_phases(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await phase_crud.get_phases(db, goal_id, current_user.id)

@router.post("/goal/{goal_id}/phases", response_model=PhaseRead)
async def create_phase(
    goal_id: int,
    data: PhaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    phase = await phase_crud.create_phase(db, data, goal_id, current_user.id)
    return await phase_crud.get_phase(db, phase.id, current_user.id)

@router.put("/phases/{phase_id}", response_model=PhaseRead)
async def update_phase(
    phase_id: int,
    data: PhaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await phase_crud.update_phase(db, phase_id, current_user.id, data)
    if not result:
        raise HTTPException(404, "Phase not found")
    return await phase_crud.get_phase(db, phase_id, current_user.id)

@router.delete("/phases/{phase_id}")
async def delete_phase(
    phase_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await phase_crud.delete_phase(db, phase_id, current_user.id)
    if not result:
        raise HTTPException(404, "Phase not found")
    return {"message": "deleted"}
