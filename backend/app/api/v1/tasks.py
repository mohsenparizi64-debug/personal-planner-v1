from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.crud import task as task_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

def add_computed_fields(task):
    task_read = TaskRead.model_validate(task)
    task_read.days_until_due = task_crud.calculate_days_until_due(task)
    task_read.days_until_recurrence = task_crud.calculate_days_until_recurrence(task)
    return task_read

@router.get("/", response_model=List[TaskRead])
async def get_tasks(
    skip: int = 0, 
    limit: int = 5000, # 🚀 افزایش سقف به ۵,۰۰۰ تسک جهت نمایش تمام ۱۳۶+ تسک
    category: Optional[str] = Query(None), status: Optional[str] = Query(None),
    priority: Optional[int] = Query(None), goal_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = await task_crud.get_tasks(db, current_user.id, skip, limit)
    if category: tasks = [t for t in tasks if t.category == category]
    if status: tasks = [t for t in tasks if t.status == status]
    if priority is not None: tasks = [t for t in tasks if t.priority == priority]
    if goal_id: tasks = [t for t in tasks if t.goal_id == goal_id]
    return [add_computed_fields(t) for t in tasks]

@router.post("/", response_model=TaskRead)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.create_task(db, task_in, current_user.id)
    return add_computed_fields(task)

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.update_task(db, task_id, current_user.id, task_update)
    if not task: raise HTTPException(404, "Task not found")
    return add_computed_fields(task)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await task_crud.delete_task(db, task_id, current_user.id)
    if not task: raise HTTPException(404, "Task not found")
    return {"message": "Task deleted"}

@router.get("/categories")
async def get_categories():
    return [
        {"value": "work", "label": "کاری"},
        {"value": "personal", "label": "شخصی"},
        {"value": "health", "label": "سلامتی"},
        {"value": "study", "label": "مطالعه"},
        {"value": "finance", "label": "مالی"},
        {"value": "other", "label": "سایر"},
    ]