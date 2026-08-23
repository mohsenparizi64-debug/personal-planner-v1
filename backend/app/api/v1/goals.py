from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.goal import GoalCreate, GoalUpdate, GoalRead
from app.schemas.goal_log import GoalLogRead
from app.crud import goal as goal_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/", response_model=List[GoalRead])
async def get_goals(
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await goal_crud.get_goals(db, current_user.id, skip, limit)

@router.post("/", response_model=GoalRead)
async def create_goal(
    goal_in: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await goal_crud.create_goal(db, goal_in, current_user.id)

@router.put("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = await goal_crud.update_goal(db, goal_id, current_user.id, goal_update)
    if not goal: raise HTTPException(404, "Goal not found")
    return goal

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = await goal_crud.delete_goal(db, goal_id, current_user.id)
    if not goal: raise HTTPException(404, "Goal not found")
    return {"message": "Goal deleted"}

@router.delete("/all/reset")
async def reset_all_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = await goal_crud.delete_all_goals(db, current_user.id)
    return {"message": f"{count} goals deleted"}

@router.get("/logs", response_model=List[GoalLogRead])
async def get_recent_logs(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await goal_crud.get_goal_logs(db, current_user.id, limit)

@router.get("/{goal_id}/logs", response_model=List[GoalLogRead])
async def get_goal_logs(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await goal_crud.get_goal_logs_by_goal(db, goal_id, current_user.id)