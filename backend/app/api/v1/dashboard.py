from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import random

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Task, Goal, SubGoal, Account, Idea, Transaction

router = APIRouter()

@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    today_str = today.isoformat()

    # ۱. همه تسک‌های کاربر
    tasks_result = await db.execute(
        select(Task)
        .where(Task.owner_id == current_user.id)
        .options(selectinload(Task.sub_goal), selectinload(Task.goal))
        .order_by(Task.created_at.desc())
    )
    all_tasks = tasks_result.scalars().all()

    # محاسبه آمار تسک‌ها
    today_tasks = []
    overdue_tasks = []
    fixed_tasks_count = 0
    recurring_tasks_count = 0
    recurring_completed_count = 0
    completed_today_count = 0

    for t in all_tasks:
        # تسک‌های ثابت یا دوره‌ای
        if t.recurrence_type and t.recurrence_type != 'none':
            recurring_tasks_count += 1
            if t.is_completed:
                recurring_completed_count += 1
        else:
            fixed_tasks_count += 1

        # کارهای امروز
        t_due = str(t.due_date) if t.due_date else None
        t_reg = str(t.register_date) if t.register_date else None
        t_last = str(t.last_action_date) if t.last_action_date else None

        if t_due == today_str or t_reg == today_str:
            today_tasks.append(t)
            if t.is_completed:
                completed_today_count += 1
        elif t_last == today_str and t.is_completed:
            completed_today_count += 1

        # کارهای عقب‌افتاده
        if t.due_date and t.due_date < today and not t.is_completed:
            overdue_tasks.append(t)

    # نرخ موفقیت تسک‌های دوره‌ای
    recurring_rate = round((recurring_completed_count / recurring_tasks_count * 100)) if recurring_tasks_count > 0 else 100

    # ۲. اهداف کلان و محاسبه پیشرفت واقعی
    goals_result = await db.execute(
        select(Goal)
        .where(Goal.owner_id == current_user.id)
        .options(selectinload(Goal.sub_goals), selectinload(Goal.main_tasks))
    )
    goals = goals_result.scalars().all()

    calculated_goals = []
    for g in goals:
        total_goal_tasks = len(g.main_tasks)
        completed_goal_tasks = sum(1 for t in g.main_tasks if t.is_completed)
        
        # محاسبه درصد
        calc_progress = round((completed_goal_tasks / total_goal_tasks * 100)) if total_goal_tasks > 0 else (g.progress_percent or 0)
        
        calculated_goals.append({
            "id": g.id,
            "title": g.title,
            "priority": g.priority,
            "target_date": str(g.target_date) if g.target_date else None,
            "calculated_progress": calc_progress,
            "total_tasks": total_goal_tasks,
            "completed_tasks": completed_goal_tasks,
            "next_step": g.next_step
        })

    # ۳. امور مالی
    accounts_result = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    accounts = accounts_result.scalars().all()
    total_balance = sum((getattr(a, 'current_balance', 0) or getattr(a, 'balance', 0)) for a in accounts)

    # ۴. ایده‌ها
    ideas_result = await db.execute(select(Idea).where(Idea.owner_id == current_user.id))
    ideas = ideas_result.scalars().all()
    idea_of_the_day = None
    if ideas:
        actionable_ideas = [i for i in ideas if i.status != 'archived']
        if actionable_ideas:
            selected_idea = random.choice(actionable_ideas)
            idea_of_the_day = {"id": selected_idea.id, "title": selected_idea.title, "description": selected_idea.description}

    # ۵. آمار ۷ روز گذشته برای نمودار میله‌ای
    weekly_activity = []
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_str = day_date.isoformat()
        
        completed_on_day = sum(1 for t in all_tasks if str(t.last_action_date) == day_str and t.is_completed)
        created_on_day = sum(1 for t in all_tasks if str(t.register_date) == day_str or str(t.created_at)[:10] == day_str)

        # نام روز هفته
        day_name = day_date.strftime("%a")
        weekly_activity.append({
            "date": day_str,
            "day_name": day_name,
            "completed": completed_on_day,
            "created": created_on_day
        })

    return {
        "summary": {
            "today_total": len(today_tasks),
            "today_completed": completed_today_count,
            "overdue_count": len(overdue_tasks),
            "total_tasks_count": len(all_tasks),
            "fixed_tasks_count": fixed_tasks_count,
            "recurring_tasks_count": recurring_tasks_count,
            "recurring_completion_rate": recurring_rate,
            "total_balance": total_balance,
            "total_ideas_count": len(ideas)
        },
        "today_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "is_completed": t.is_completed,
                "priority": t.priority,
                "due_date": str(t.due_date) if t.due_date else None,
                "category": t.category
            } for t in today_tasks
        ],
        "overdue_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": str(t.due_date) if t.due_date else None,
                "priority": t.priority
            } for t in overdue_tasks
        ],
        "goals": calculated_goals,
        "weekly_activity": weekly_activity,
        "idea_of_the_day": idea_of_the_day
    }