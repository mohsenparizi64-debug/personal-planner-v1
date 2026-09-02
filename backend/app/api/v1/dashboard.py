from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import hashlib

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import (
    User, Task, Goal, SubGoal, Account, Idea, Transaction, 
    Movie, Book, Place, HealthLog, WorkoutLog, MealLog, SpiritualTracker
)

router = APIRouter()

# نگاشت روزهای هفته به تقویم شمسی ایرانی (شروع اکید از شنبه)
def get_persian_day_name(d: date) -> str:
    # d.weekday(): 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    mapping = {
        5: "شنبه",
        6: "یکشنبه",
        0: "دوشنبه",
        1: "سه‌شنبه",
        2: "چهارشنبه",
        3: "پنج‌شنبه",
        4: "جمعه"
    }
    return mapping.get(d.weekday(), "شنبه")

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

    # آمار دقیق تسک‌های یک‌باره و دوره‌ای
    today_tasks = []
    overdue_tasks = []
    fixed_tasks_count = 0
    fixed_completed_count = 0
    recurring_tasks_count = 0
    recurring_completed_count = 0
    
    category_counts = {}

    for t in all_tasks:
        cat = t.category or "عمومی"
        category_counts[cat] = category_counts.get(cat, 0) + 1

        # تفکیک دقیق تسک‌های یک‌باره و دوره‌ای
        if t.recurrence_type and t.recurrence_type != 'none':
            recurring_tasks_count += 1
            # سنجش تحقق تسک‌های دوره‌ای بر اساس اقدام در دوره جاری
            if t.is_completed or str(t.last_action_date) == today_str:
                recurring_completed_count += 1
        else:
            fixed_tasks_count += 1
            if t.is_completed:
                fixed_completed_count += 1

        # کارهای امروز (همگام‌سازی دقیق صورت و مخرج)
        t_due = str(t.due_date) if t.due_date else None
        t_reg = str(t.register_date) if t.register_date else None
        t_last = str(t.last_action_date) if t.last_action_date else None

        if t_due == today_str or t_reg == today_str or t_last == today_str:
            today_tasks.append(t)

        # کارهای عقب‌افتاده
        if t.due_date and t.due_date < today and not t.is_completed:
            overdue_tasks.append(t)

    # همگام‌سازی تعداد کارهای انجام‌شده امروز
    completed_today_count = sum(1 for t in today_tasks if t.is_completed or str(t.last_action_date) == today_str)

    # نرخ‌های واقعی موفقیت
    recurring_rate = round((recurring_completed_count / recurring_tasks_count * 100)) if recurring_tasks_count > 0 else 100
    fixed_rate = round((fixed_completed_count / fixed_tasks_count * 100)) if fixed_tasks_count > 0 else 100

    # ۲. فرمول وزن‌دهی پیشرفت اهداف کلان (تقسیم بر تعداد گام‌های عملیاتی SubGoals)
    goals_result = await db.execute(
        select(Goal)
        .where(Goal.owner_id == current_user.id)
        .options(selectinload(Goal.sub_goals), selectinload(Goal.main_tasks))
    )
    goals = goals_result.scalars().all()

    calculated_goals = []
    for g in goals:
        sub_goals_count = len(g.sub_goals)
        
        if sub_goals_count > 0:
            # میانگین پیشرفت واقعی گام‌های عملیاتی
            total_sub_progress = sum(sg.progress_percent or 0 for sg in g.sub_goals)
            calc_progress = round(total_sub_progress / sub_goals_count)
        else:
            # در صورت عدم وجود گام عملیاتی، سنجش بر اساس تسک‌های مستقیم یا درصد دستی
            total_tasks = len(g.main_tasks)
            completed_tasks = sum(1 for t in g.main_tasks if t.is_completed)
            calc_progress = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else (g.progress_percent or 0)
        
        calculated_goals.append({
            "id": g.id,
            "title": g.title,
            "priority": g.priority,
            "target_date": str(g.target_date) if g.target_date else None,
            "calculated_progress": min(100, max(0, calc_progress)),
            "sub_goals_count": sub_goals_count,
            "next_step": g.next_step
        })

    # ۳. امور مالی
    accounts_result = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    accounts = accounts_result.scalars().all()
    total_balance = sum((getattr(a, 'current_balance', 0) or getattr(a, 'balance', 0)) for a in accounts)

    # ۴. الگوریتم هوشمند انتخاب ایده برتر روز (ثابت در طول روز + هیجان بالا)
    ideas_result = await db.execute(select(Idea).where(Idea.owner_id == current_user.id))
    ideas = ideas_result.scalars().all()
    idea_of_the_day = None
    if ideas:
        # فیلتر ایده‌های فعال و با هیجان ۴ یا ۵ ستاره
        top_ideas = [i for i in ideas if i.status != 'archived' and (i.excitement_rating or 3) >= 4]
        if not top_ideas:
            top_ideas = [i for i in ideas if i.status != 'archived']
            
        if top_ideas:
            # الگوریتم هش قطعی روزانه برای ثبات ایده در طول ۲۴ ساعت
            seed_str = f"{today_str}_{current_user.id}"
            hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
            selected_idea = top_ideas[hash_val % len(top_ideas)]
            idea_of_the_day = {
                "id": selected_idea.id, 
                "title": selected_idea.title, 
                "description": selected_idea.description,
                "excitement_rating": selected_idea.excitement_rating
            }

    # ۵. آمار ۷ روز هفته جاری (شنبه تا جمعه) با تقویم فارسی
    weekly_activity = []
    # ابتدا شنبه همین هفته رو پیدا کن
    # weekday(): 0=Mon..6=Sun. شنبه = 5
    days_since_saturday = (today.weekday() - 5) % 7
    saturday = today - timedelta(days=days_since_saturday)
    for i in range(7):
        day_date = saturday + timedelta(days=i)
        day_str = day_date.isoformat()

        # تعریف واحد "تکمیل‌شده در روز X" (مثل completed_on_day):
        #   - تسک تکمیل‌شده (is_completed) و due_date == day_str
        #   - یا last_action_date == day_str
        def _is_completed_on_day(t):
            if not t:
                return False
            if t.is_completed and str(t.due_date) == day_str:
                return True
            if str(t.last_action_date) == day_str:
                return True
            return False

        # تفکیک دقیق: ثابت (fixed) و دوره‌ای (recurring) برای آن روز
        is_fixed = lambda t: (t.recurrence_type in (None, '', 'none'))
        is_recurring = lambda t: (t.recurrence_type and t.recurrence_type != 'none')

        fixed_count = sum(1 for t in all_tasks if is_fixed(t) and _is_completed_on_day(t))
        recurring_count = sum(1 for t in all_tasks if is_recurring(t) and _is_completed_on_day(t))

        completed_on_day = fixed_count + recurring_count
        created_on_day = sum(1 for t in all_tasks if str(t.register_date) == day_str or str(t.created_at)[:10] == day_str)

        day_name = get_persian_day_name(day_date)
        weekly_activity.append({
            "date": day_str,
            "day_name": day_name,
            "completed": completed_on_day,
            "created": created_on_day,
            "fixed_completed": fixed_count,
            "recurring_completed": recurring_count,
        })

    return {
        "summary": {
            "today_total": len(today_tasks),
            "today_completed": completed_today_count,
            "overdue_count": len(overdue_tasks),
            "total_tasks_count": len(all_tasks),
            "fixed_tasks_count": fixed_tasks_count,
            "fixed_completed_count": fixed_completed_count,
            "fixed_completion_rate": fixed_rate,
            "recurring_tasks_count": recurring_tasks_count,
            "recurring_completed_count": recurring_completed_count,
            "recurring_completion_rate": recurring_rate,
            "total_balance": total_balance,
            "total_ideas_count": len(ideas),
            "category_breakdown": category_counts
        },
        "today_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "is_completed": t.is_completed or (str(t.last_action_date) == today_str),
                "priority": t.priority,
                "due_date": str(t.due_date) if t.due_date else None,
                "category": t.category,
                "description": t.description,
                "goal_title": t.goal.title if t.goal else "عمومی"
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

# ای‌پیوآی جدید هاب تحلیلی برج دیده‌بانی (پوشش کامل تمام ورودی/خروجی‌های سیستم)
@router.get("/analytics")
async def get_analytics(
    days: int = Query(default=7, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    start_date = today - timedelta(days=days)

    # ۱. تحلیل تسک‌ها به تفکیک اهداف کلان
    goals_res = await db.execute(
        select(Goal)
        .where(Goal.owner_id == current_user.id)
        .options(selectinload(Goal.main_tasks))
    )
    goals = goals_res.scalars().all()
    goal_analytics = []
    for g in goals:
        completed_in_period = sum(
            1 for t in g.main_tasks 
            if t.is_completed and t.last_action_date and t.last_action_date >= start_date
        )
        goal_analytics.append({
            "goal_id": g.id,
            "title": g.title,
            "completed_tasks": completed_in_period,
            "total_tasks": len(g.main_tasks)
        })

    # ۲. روند مالی واریزی و برداشت
    tx_res = await db.execute(
        select(Transaction)
        .where(Transaction.owner_id == current_user.id)
    )
    transactions = tx_res.scalars().all()
    deposit_total = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
    withdraw_total = sum(t.amount for t in transactions if t.transaction_type == 'withdraw')

    # ۳. روند وزن و کالری
    health_res = await db.execute(
        select(HealthLog)
        .where(HealthLog.owner_id == current_user.id, HealthLog.log_date >= start_date)
        .order_by(HealthLog.log_date.asc())
    )
    health_logs = health_res.scalars().all()
    weight_trend = [{"date": str(h.log_date), "weight": h.weight} for h in health_logs if h.weight]

    # ۴. سبک زندگی
    movies_cnt = (await db.execute(select(func.count(Movie.id)).where(Movie.owner_id == current_user.id, Movie.is_watched == True))).scalar() or 0
    books_cnt = (await db.execute(select(func.count(Book.id)).where(Book.owner_id == current_user.id, Book.is_read == True))).scalar() or 0
    places_cnt = (await db.execute(select(func.count(Place.id)).where(Place.owner_id == current_user.id, Place.is_visited == True))).scalar() or 0

    return {
        "period_days": days,
        "goal_analytics": goal_analytics,
        "financial_summary": {
            "deposit_total": deposit_total,
            "withdraw_total": withdraw_total,
            "balance_net": deposit_total - withdraw_total
        },
        "weight_trend": weight_trend,
        "lifestyle_summary": {
            "movies_watched": movies_cnt,
            "books_read": books_cnt,
            "places_visited": places_cnt
        }
    }