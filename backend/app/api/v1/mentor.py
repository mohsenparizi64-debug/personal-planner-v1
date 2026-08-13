from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Tuple, Optional
from datetime import date, datetime, timedelta
import os
import httpx
import json

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.all_models import User, Task, Goal, SubGoal, Account, Idea

router = APIRouter()

AVALAI_API_URL = "https://api.avalai.ir/v1/chat/completions"

def build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas, time_days: int = 7):
    """ساخت فایل جامع دیتابیس با درک کامل از معماری سه‌لایه‌ای (اهداف ➔ گام‌ها ➔ تسک‌ها)"""
    today = date.today()
    today_str = today.isoformat()
    start_time_frame = today - timedelta(days=time_days)
    start_time_frame_str = start_time_frame.isoformat()

    # ۱. دسته‌بندی تسک‌ها در بازه زمانی انتخابی
    time_frame_acted_tasks = []
    overdue_tasks = []
    completed_tasks = []
    
    for t in tasks:
        t_due = str(t.due_date) if t.due_date else None
        t_last = str(t.last_action_date) if t.last_action_date else None

        if t.is_completed or t.status == 'completed':
            completed_tasks.append(t)
            if t_last and t_last >= start_time_frame_str:
                time_frame_acted_tasks.append(t)
        else:
            if t_due and t_due < today_str:
                overdue_tasks.append(t)
            if t_last and t_last >= start_time_frame_str:
                time_frame_acted_tasks.append(t)

    # ۲. تحلیل عمیق اهداف کلان و میزان وقت/تسک‌های اختصاص داده‌شده
    goals_data = []
    neglected_goals = []

    for g in goals:
        # تمام تسک‌های متصل به این هدف کلان
        g_tasks = g.main_tasks if hasattr(g, 'main_tasks') and g.main_tasks else []
        total_g_tasks = len(g_tasks)
        comp_g_tasks = sum(1 for t in g_tasks if t.is_completed)
        
        # تسک‌های انجام‌شده این هدف در بازه زمانی انتخابی
        acted_in_timeframe = [t for t in g_tasks if t.last_action_date and str(t.last_action_date) >= start_time_frame_str]
        
        calc_prog = round((comp_g_tasks / total_g_tasks * 100)) if total_g_tasks > 0 else (g.progress_percent or 0)
        
        goal_info = {
            "id": g.id,
            "title": g.title,
            "priority": "فوری" if g.priority == 2 else "مهم" if g.priority == 1 else "عادی",
            "progress": f"{calc_prog}%",
            "total_tasks_count": total_g_tasks,
            "completed_tasks_count": comp_g_tasks,
            "acted_tasks_in_timeframe": len(acted_in_timeframe),
            "obstacle": g.current_obstacle or "ذکر نشده",
            "next_step": g.next_step or "تعیین نشده",
            "success_criteria": g.success_criteria or "تعیین نشده"
        }
        goals_data.append(goal_info)

        # اگر در این بازه زمانی هیچ اقدامی برای هدف نشده باشد یا تسک‌هایش ۰ باشد، هدف کم‌توجه/رهاشده است
        if len(acted_in_timeframe) == 0 and not g.is_completed:
            neglected_goals.append(goal_info)

    total_balance = sum((getattr(a, 'current_balance', 0) or getattr(a, 'balance', 0)) for a in accounts)

    return {
        "architecture_summary": "معماری سه‌لایه‌ای: ۱. اهداف کلان (استراتژیک) ➔ ۲. گام‌های نقشه راه (تاکتیکی) ➔ ۳. تسک‌های ۱۱ فیلدی (عملیاتی)",
        "today_date": today_str,
        "time_frame_days": time_days,
        "user_summary": {
            "total_goals_count": len(goals),
            "neglected_goals_count": len(neglected_goals),
            "total_tasks_count": len(tasks),
            "acted_tasks_in_timeframe_count": len(time_frame_acted_tasks),
            "overdue_tasks_count": len(overdue_tasks),
            "total_financial_balance": f"{total_balance:,} تومان",
            "total_ideas_count": len(ideas)
        },
        "goals": goals_data,
        "neglected_goals": neglected_goals,
        "overdue_tasks_list": [{"title": t.title, "due_date": str(t.due_date)} for t in overdue_tasks[:10]]
    }

async def call_avalai_ai(system_prompt: str, user_prompt: str) -> Tuple[Optional[str], str]:
    """فراخوانی هوش مصنوعی زنده AvalAI"""
    api_key = os.getenv("AVALAI_API_KEY") or getattr(settings, "AVALAI_API_KEY", "")
    
    if not api_key or "کپی_شده" in api_key:
        err_msg = "⚠️ کلید AVALAI_API_KEY در config.py تنظیم نشده است."
        return None, err_msg

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(AVALAI_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"], "OK"
            else:
                return None, f"❌ خطای سرویس AvalAI (کد {response.status_code}): {response.text}"
    except Exception as e:
        return None, f"❌ خطای شبکه: {str(e)}"

@router.get("/report")
async def generate_mentor_report(
    time_frame: str = Query("last_1_week"), # last_3_days, last_1_week, last_2_weeks, last_1_month
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تولید گزارش تشخیصی هوشمند منتور با انتخاب بازه زمانی"""
    time_days = 3 if time_frame == "last_3_days" else 14 if time_frame == "last_2_weeks" else 30 if time_frame == "last_1_month" else 7
    time_frame_label = "۳ روز گذشته" if time_frame == "last_3_days" else "۲ هفته گذشته" if time_frame == "last_2_weeks" else "۱ ماه گذشته" if time_frame == "last_1_month" else "۱ هفته گذشته"

    tasks_res = await db.execute(select(Task).where(Task.owner_id == current_user.id))
    tasks = tasks_res.scalars().all()
    
    goals_res = await db.execute(select(Goal).where(Goal.owner_id == current_user.id).options(selectinload(Goal.main_tasks)))
    goals = goals_res.scalars().all()
    
    subgoals_res = await db.execute(select(SubGoal).where(SubGoal.owner_id == current_user.id))
    subgoals = subgoals_res.scalars().all()

    accounts_res = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    accounts = accounts_res.scalars().all()

    ideas_res = await db.execute(select(Idea).where(Idea.owner_id == current_user.id))
    ideas = ideas_res.scalars().all()

    context = build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas, time_days)

    # 🌟 پرامپت اختصاصی با نگارش شکیل، شخصیت کارشناس موضوعی و درک سه‌لایه‌ای
    system_prompt = f"""شما یک «منتور استراتژیک ارشد» و همزمان یک «کارشناس تخصصی موضوعی» برای کاربر به نام '{current_user.full_name or "کاربر گرامی"}' هستید.

معماری برنامه پلنر شخصی بر پایه ۳ لایه است:
۱. اهداف کلان (Goal): استراتژیک
۲. گام‌های نقشه راه (SubGoal): تاکتیکی
۳. تسک‌های ۱۱ فیلدی (Task): عملیاتی

اطلاعات زنده دیتابیس در بازه زمانی «{time_frame_label}»:
--- داده‌های دیتابیس ---
{json.dumps(context, ensure_ascii=False, indent=2)}
--- پایان داده‌ها ---

دستورالعمل نگارش گزارش:
۱. گزارش را با نگارش فوق‌العاده مرتب، با تیترهای مشخص (###) و بالت‌پوینت (*) بنویسید.
۲. عملکرد کاربر در «{time_frame_label}» را بررسی کنید: کدام اهداف بیشترین زمان/تسک را گرفته‌اند و کدام اهداف کم‌توجه و رهاشده مانده‌اند.
۳. برای اهداف اصلی، علاوه بر منتورینگ، نقش «کارشناس تخصصی همان حوزه» را ایفا کرده و توصیه فنی بدهید.
۴. راهکار عملی برای جبران اهداف کم‌توجه ارائه دهید."""

    ai_analysis, status_msg = await call_avalai_ai(system_prompt, f"لطفاً گزارش تحلیل عملکرد من در {time_frame_label} را ارائه دهید.")

    overdue_cnt = context["user_summary"]["overdue_tasks_count"]
    health_status = "عالی 🚀" if overdue_cnt == 0 else "نیازمند مدیریت 🚨" if overdue_cnt > 3 else "خوب ⚡"

    if ai_analysis:
        insights = [ai_analysis]
        recommendations = ["گزارش فوق بر اساس تحلیل عمیق دیتابیس صادر گردید."]
    else:
        insights = [
            f"🚨 تعداد {overdue_cnt} کار عقب‌افتاده دارید.",
            f"⚠️ تعداد {len(context['neglected_goals'])} هدف کلان در بازه {time_frame_label} کم‌توجه مانده‌اند.",
            f"وضعیت اتصال به هوش مصنوعی: {status_msg}"
        ]
        recommendations = ["لطفاً کلید AVALAI_API_KEY را در config.py تنظیم کنید."]

    return {
        "user_name": current_user.full_name or "کاربر گرامی",
        "health_status": health_status,
        "time_frame_label": time_frame_label,
        "context_summary": context["user_summary"],
        "neglected_goals": context["neglected_goals"],
        "insights": insights,
        "recommendations": recommendations
    }

@router.post("/chat")
async def mentor_chat(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """پاسخگویی هوشمند منتور در چت تعاملی"""
    user_message = payload.get("message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="متن پیام نمی‌تواند خالی باشد.")

    tasks_res = await db.execute(select(Task).where(Task.owner_id == current_user.id))
    tasks = tasks_res.scalars().all()
    
    goals_res = await db.execute(select(Goal).where(Goal.owner_id == current_user.id).options(selectinload(Goal.main_tasks)))
    goals = goals_res.scalars().all()

    subgoals_res = await db.execute(select(SubGoal).where(SubGoal.owner_id == current_user.id))
    subgoals = subgoals_res.scalars().all()

    accounts_res = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    accounts = accounts_res.scalars().all()

    ideas_res = await db.execute(select(Idea).where(Idea.owner_id == current_user.id))
    ideas = ideas_res.scalars().all()

    context = build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas)

    system_prompt = f"""شما منتور استراتژیک و کارشناس تخصصی مسلط به زندگی کاربر هستید.
داده‌های دیتابیس:
{json.dumps(context, ensure_ascii=False)}

دستورالعمل: با ساختار مرتب، تیترها و فونت ناظر بر پاسخ کاربر صحبت کنید."""

    ai_reply, status_msg = await call_avalai_ai(system_prompt, user_message)

    if not ai_reply:
        ai_reply = f"{status_msg}"

    return {
        "reply": ai_reply,
        "timestamp": datetime.now().isoformat()
    }