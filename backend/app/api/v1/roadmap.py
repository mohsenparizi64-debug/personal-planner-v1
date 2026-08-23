from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.sub_goal import SubGoalCreate, SubGoalUpdate, SubGoalRead, SubGoalTaskCreate, SubGoalTaskUpdate, SubGoalTaskRead
from app.schemas.kpi import KPICreate, KPIUpdate, KPIRead
from app.crud import roadmap as roadmap_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/goal/{goal_id}/subgoals", response_model=List[SubGoalRead])
async def get_sub_goals(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await roadmap_crud.get_sub_goals(db, goal_id, current_user.id)

@router.post("/goal/{goal_id}/subgoals", response_model=SubGoalRead)
async def create_sub_goal(
    goal_id: int,
    data: SubGoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub_goal = await roadmap_crud.create_sub_goal(db, data, goal_id, current_user.id)
    return await roadmap_crud.get_sub_goal_by_id(db, sub_goal.id, current_user.id)

@router.put("/subgoals/{sub_goal_id}", response_model=SubGoalRead)
async def update_sub_goal(
    sub_goal_id: int,
    data: SubGoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.update_sub_goal(db, sub_goal_id, current_user.id, data)
    if not result: raise HTTPException(404, "SubGoal not found")
    return await roadmap_crud.get_sub_goal_by_id(db, sub_goal_id, current_user.id)

@router.delete("/subgoals/{sub_goal_id}")
async def delete_sub_goal(
    sub_goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.delete_sub_goal(db, sub_goal_id, current_user.id)
    if not result: raise HTTPException(404, "SubGoal not found")
    return {"message": "deleted"}

@router.post("/subgoals/{sub_goal_id}/tasks", response_model=SubGoalTaskRead)
async def create_sub_task(
    sub_goal_id: int,
    data: SubGoalTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await roadmap_crud.create_sub_task(db, data, sub_goal_id, current_user.id)

@router.put("/tasks/{task_id}", response_model=SubGoalTaskRead)
async def update_sub_task(
    task_id: int,
    data: SubGoalTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.update_sub_task(db, task_id, current_user.id, data)
    if not result: raise HTTPException(404, "Task not found")
    return result

@router.delete("/tasks/{task_id}")
async def delete_sub_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.delete_sub_task(db, task_id, current_user.id)
    if not result: raise HTTPException(404, "Task not found")
    return {"message": "deleted"}

@router.get("/goal/{goal_id}/kpis", response_model=List[KPIRead])
async def get_kpis(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await roadmap_crud.get_kpis(db, goal_id, current_user.id)

@router.post("/goal/{goal_id}/kpis", response_model=KPIRead)
async def create_kpi(
    goal_id: int,
    data: KPICreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await roadmap_crud.create_kpi(db, data, goal_id, current_user.id)

@router.put("/kpis/{kpi_id}", response_model=KPIRead)
async def update_kpi(
    kpi_id: int,
    data: KPIUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.update_kpi(db, kpi_id, current_user.id, data)
    if not result: raise HTTPException(404, "KPI not found")
    return result

@router.delete("/kpis/{kpi_id}")
async def delete_kpi(
    kpi_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await roadmap_crud.delete_kpi(db, kpi_id, current_user.id)
    if not result: raise HTTPException(404, "KPI not found")
    return {"message": "deleted"}