from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Idea, Goal, Task
from app.schemas.idea import IdeaCreate, IdeaRead, IdeaUpdate

router = APIRouter()

@router.get("", response_model=List[IdeaRead])
async def get_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.owner_id == current_user.id).order_by(Idea.id.desc())
    )
    return result.scalars().all()

@router.post("", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
async def create_idea(
    idea_in: IdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    idea = Idea(**idea_in.model_dump(), owner_id=current_user.id)
    db.add(idea)
    await db.commit()
    await db.refresh(idea)
    return idea

@router.put("/{idea_id}", response_model=IdeaRead)
async def update_idea(
    idea_id: int,
    idea_in: IdeaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.owner_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="ایده یافت نشد")

    update_data = idea_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(idea, field, value)

    await db.commit()
    await db.refresh(idea)
    return idea

@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.owner_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="ایده یافت نشد")

    await db.delete(idea)
    await db.commit()

# ========================================================
# قابلیت جادویی ۱: تبدیل ایده پخته به هدف کلان (Goal)
# ========================================================
@router.post("/{idea_id}/convert-to-goal")
async def convert_idea_to_goal(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.owner_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="ایده یافت نشد")

    # ساخت هدف جدید از روی اطلاعات ایده
    new_goal = Goal(
        title=idea.title,
        description=f"ساخته شده از روی ایده:\n{idea.description or ''}",
        priority=idea.excitement_rating,
        owner_id=current_user.id
    )
    db.add(new_goal)
    await db.flush()

    # به‌روزرسانی وضعیت ایده
    idea.converted_to_goal_id = new_goal.id
    idea.status = "ready"
    await db.commit()

    return {"message": "ایده با موفقیت به هدف کلان تبدیل شد", "goal_id": new_goal.id}

# ========================================================
# قابلیت جادویی ۲: تبدیل ایده به تسک اجرایی (Task)
# ========================================================
@router.post("/{idea_id}/convert-to-task")
async def convert_idea_to_task(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id, Idea.owner_id == current_user.id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="ایده یافت نشد")

    new_task = Task(
        title=idea.title,
        description=f"ساخته شده از روی ایده:\n{idea.description or ''}",
        category=idea.category,
        priority=idea.excitement_rating,
        goal_id=idea.goal_id,
        owner_id=current_user.id
    )
    db.add(new_task)
    await db.flush()

    idea.converted_to_task_id = new_task.id
    idea.status = "ready"
    await db.commit()

    return {"message": "ایده با موفقیت به تسک اجرایی تبدیل شد", "task_id": new_task.id}