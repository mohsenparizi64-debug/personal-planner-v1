from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Idea, Goal, Task, SubGoal
from app.schemas.idea import IdeaCreate, IdeaRead, IdeaUpdate

router = APIRouter()

# دریافت ایده‌ها با استعلام زنده آخرین وضعیت تسک/هدف تبدیل‌شده
@router.get("", response_model=List[IdeaRead])
async def get_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Idea).where(Idea.owner_id == current_user.id).order_by(Idea.id.desc())
    )
    ideas = result.scalars().all()
    
    ideas_response = []
    for idea in ideas:
        idea_dict = IdeaRead.model_validate(idea).model_dump()
        live_info = {"is_converted": False, "is_completed": False, "target_type": None, "status_text": "خام"}
        
        # ۱. اگر ایده به تسک تبدیل شده است
        if idea.converted_to_task_id:
            live_info["is_converted"] = True
            live_info["target_type"] = "task"
            t_res = await db.execute(select(Task).where(Task.id == idea.converted_to_task_id))
            t = t_res.scalar_one_or_none()
            if t:
                live_info["is_completed"] = t.is_completed
                live_info["status_text"] = "تکمیل و محقق شده 🎉" if t.is_completed else ("در حال انجام" if t.status == 'in_progress' else "در دست اقدام")
                live_info["target_title"] = t.title
        
        # ۲. اگر ایده به هدف تبدیل شده است
        elif idea.converted_to_goal_id:
            live_info["is_converted"] = True
            live_info["target_type"] = "goal"
            g_res = await db.execute(select(Goal).where(Goal.id == idea.converted_to_goal_id))
            g = g_res.scalar_one_or_none()
            if g:
                live_info["is_completed"] = g.is_completed
                live_info["status_text"] = "هدف محقق شده 🏆" if g.is_completed else f"در حال اجرا ({g.progress_percent or 0}٪)"
                live_info["target_title"] = g.title
                
        idea_dict["live_status_info"] = live_info
        ideas_response.append(idea_dict)

    return ideas_response

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

# تبدیل هوشمند ایده به هدف کلان با ثبت شناسه ایده در شناسه هدف
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

    new_goal = Goal(
        title=idea.title,
        description=f"💡 زاده شده از ایده شماره #{idea.id}:\n{idea.description or ''}",
        priority=idea.excitement_rating,
        owner_id=current_user.id
    )
    db.add(new_goal)
    await db.flush()

    idea.converted_to_goal_id = new_goal.id
    idea.conversion_date = date.today()
    idea.status = "ready"
    await db.commit()

    return {"message": "ایده با موفقیت به هدف کلان تبدیل شد", "goal_id": new_goal.id}

# تبدیل هوشمند ایده به تسک با حفظ کامل Goal ID و SubGoal ID
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
        description=f"💡 زاده شده از ایده شماره #{idea.id}:\n{idea.description or ''}",
        category=idea.category,
        priority=idea.excitement_rating,
        goal_id=idea.goal_id,
        sub_goal_id=idea.sub_goal_id,
        owner_id=current_user.id
    )
    db.add(new_task)
    await db.flush()

    idea.converted_to_task_id = new_task.id
    idea.conversion_date = date.today()
    idea.status = "ready"
    await db.commit()

    return {"message": "ایده با موفقیت به تسک اجرایی تبدیل شد", "task_id": new_task.id}