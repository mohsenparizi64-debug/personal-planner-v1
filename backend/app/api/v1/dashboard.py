from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Task, Goal, SubGoal, SubGoalTask
from app.schemas.task import TaskRead
from app.crud import task as task_crud

router = APIRouter()

@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # همه تسک‌ها با رابطه
    tasks_result = await db.execute(
        select(Task)
        .where(Task.owner_id == current_user.id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.created_at.desc())
    )
    tasks = tasks_result.scalars().all()
    print(f"DEBUG: User {current_user.id} has {len(tasks)} tasks")
    
    # همه اهداف
    goals_result = await db.execute(
        select(Goal).where(Goal.owner_id == current_user.id)
    )
    goals = goals_result.scalars().all()
    
    # همه زیرهدف‌ها با تسک‌هاشون
    subgoals_result = await db.execute(
        select(SubGoal)
        .where(SubGoal.owner_id == current_user.id)
        .options(selectinload(SubGoal.linked_tasks))
    )
    subgoals = subgoals_result.scalars().all()
    
    return {
        "tasks": [
            {
                "id": t.id, "title": t.title, "status": t.status,
                "priority": t.priority, "due_date": t.due_date,
                "goal_id": t.goal_id, "sub_goal_id": t.sub_goal_id,
                "goal_title": t.goal.title if t.goal else None,
                "sub_goal_title": t.sub_goal.title if t.sub_goal else None,
            }
            for t in tasks
        ],
        "goals": [{"id": g.id, "title": g.title} for g in goals],
        "subgoals": [
            {
                "id": sg.id, "title": sg.title, "goal_id": sg.goal_id,
                "tasks": [{"id": t.id, "title": t.title, "is_completed": t.is_completed} for t in sg.linked_tasks]
            }
            for sg in subgoals
        ]
    }