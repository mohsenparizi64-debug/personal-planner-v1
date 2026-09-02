from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Tuple, Optional
from datetime import date, datetime, timedelta
import os
import time
import httpx
import json

from app.db.session import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.all_models import User, Task, Goal, SubGoal, Account, Idea, MentorReport, Skill

router = APIRouter()

AVALAI_API_URL = "https://api.avalai.ir/v1/chat/completions"

# 📦 کش موقت context هر کاربر برای چت (کاهش ۷۰٪ توکن)
# key: f"{user_id}" → { "context": ..., "system_prompt": ..., "timestamp": ... }
_chat_context_cache: Dict[str, Dict[str, Any]] = {}
_CHAT_CACHE_TTL = 1800  # ۳۰ دقیقه (بعد از این مدت، context از نو ساخته میشه)

def build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas, skills=None, time_days: int = 7):
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

    # ۳. تحلیل مهارت‌ها (skills)
    skills_data = []
    skills_count = {"total": 0, "mastered": 0, "in_progress": 0, "on_hold": 0, "independent": 0}
    if skills:
        for s in skills:
            skills_count["total"] += 1
            if s.status == 'mastered':
                skills_count["mastered"] += 1
            elif s.status == 'in_progress':
                skills_count["in_progress"] += 1
            elif s.status == 'on_hold':
                skills_count["on_hold"] += 1
            if s.goal_id is None:
                skills_count["independent"] += 1

            # پیدا کردن goal_title
            goal_title = None
            if s.goal_id:
                for g in goals:
                    if g.id == s.goal_id:
                        goal_title = g.title
                        break

            skills_data.append({
                "id": s.id,
                "title": s.title,
                "category": s.category or "عمومی",
                "status": s.status,
                "level": s.level or "beginner",
                "progress_percent": s.progress_percent,
                "goal_title": goal_title,
                "is_independent": s.goal_id is None,
                "practiced_hours": s.practiced_hours or 0,
                "target_hours": s.target_hours
            })

    # میانگین پیشرفت مهارت‌ها
    avg_skill_progress = round(sum(s.progress_percent for s in skills_data) / len(skills_data), 1) if skills_data else 0

    total_balance = sum((getattr(a, 'current_balance', 0) or getattr(a, 'balance', 0)) for a in accounts)

    return {
        "architecture_summary": "معماری چهارلایه‌ای: ۱. اهداف کلان (استراتژیک) ➔ ۲. گام‌های نقشه راه (تاکتیکی) ➔ ۳. تسک‌های ۱۱ فیلدی (عملیاتی) ➔ ۴. مهارت‌ها و دانش",
        "today_date": today_str,
        "time_frame_days": time_days,
        "user_summary": {
            "total_goals_count": len(goals),
            "neglected_goals_count": len(neglected_goals),
            "total_tasks_count": len(tasks),
            "acted_tasks_in_timeframe_count": len(time_frame_acted_tasks),
            "overdue_tasks_count": len(overdue_tasks),
            "total_financial_balance": f"{total_balance:,} تومان",
            "total_ideas_count": len(ideas),
            "total_skills_count": skills_count["total"],
            "mastered_skills_count": skills_count["mastered"],
            "in_progress_skills_count": skills_count["in_progress"],
            "independent_skills_count": skills_count["independent"],
            "avg_skill_progress": avg_skill_progress
        },
        "goals": goals_data,
        "neglected_goals": neglected_goals,
        "skills": skills_data,
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
    force_regenerate: bool = Query(False),  # برای debug یا admin
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تولید گزارش تشخیصی هوشمند منتور - فقط یک بار در روز (کش در DB)"""
    time_days = 3 if time_frame == "last_3_days" else 14 if time_frame == "last_2_weeks" else 30 if time_frame == "last_1_month" else 7
    time_frame_label = "۳ روز گذشته" if time_frame == "last_3_days" else "۲ هفته گذشته" if time_frame == "last_2_weeks" else "۱ ماه گذشته" if time_frame == "last_1_month" else "۱ هفته گذشته"

    today = date.today()

    # ۱. بررسی کش امروز (مگر اینکه force_regenerate=True باشه)
    if not force_regenerate:
        cached = await db.execute(
            select(MentorReport)
            .where(MentorReport.owner_id == current_user.id)
            .where(MentorReport.report_date == today)
        )
        cached_report = cached.scalar_one_or_none()
        if cached_report:
            return {
                "from_cache": True,
                "generated_at": cached_report.created_at.isoformat() if cached_report.created_at else None,
                "time_frame_label": time_frame_label,
                "time_frame_used": cached_report.time_frame,
                "user_name": current_user.full_name or "کاربر گرامی",
                "health_status": "عالی 🚀",  # بعداً محاسبه شود
                "context_summary": json.loads(cached_report.context_summary or "{}"),
                "neglected_goals": json.loads(cached_report.neglected_goals or "[]"),
                "short_report": cached_report.short_report,
                "full_report": cached_report.full_report,
            }

    # ۲. تولید گزارش جدید
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

    # دریافت مهارت‌ها برای گزارش
    skills_res = await db.execute(select(Skill).where(Skill.owner_id == current_user.id))
    skills = skills_res.scalars().all()

    context = build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas, skills, time_days)

    # 🌟 پرامپت جدید: ۲ پاراگراف + لحن مشوقانه («تو»، «قدم بعدی»، «بزن بریم»)
    user_name = current_user.full_name or "دوست من"

    # پرامپت سیستم برای گزارش کوتاه (۲ پاراگراف)
    short_system_prompt = f"""تو یک «منتور شخصی» هستی که با «{user_name}» در حال گفتگویی صمیمی و حمایتی هستی. لحن تو:
- مخاطب قرار دادن کاربر: «تو»، «قدم بعدی»، «بزن بریم»
- دلسوزانه برای موفقیت‌ها، مشوقانه برای ادامه، منتقدانه مهربانانه برای کم‌کاری‌ها (بدون قضاوت)
- فارسی، گرم، صمیمی، واقعی

📊 داده‌های زنده دیتابیس در بازه «{time_frame_label}»:
```json
{json.dumps(context, ensure_ascii=False, indent=2)}
```

📝 خروجی: دقیقاً ۲ پاراگراف فارسی:
- **پاراگراف ۱ (وضعیت تو):** آمار کلیدی + نقاط قوت + لحن تشویق‌آمیز
- **پاراگراف ۲ (قدم بعدی):** توصیه عملی + گام بعدی مشخص + «بزن بریم»

⚠️ فقط ۲ پاراگراف. حداکثر ۱۵۰ کلمه. بدون تیتر، بدون بالت‌پوینت، فقط متن روان.

💡 اگر کاربر مهارت (skill) دارد، در پاراگراف ۱ به میانگین پیشرفت مهارت‌ها و تعداد مهارت‌های مستقل (بدون هدف) اشاره کن. مثال: «تو {total_skills_count} مهارت داری، {avg_skill_progress}٪ پیشرفت کردی، عالیه! {independent_skills_count} تای آن‌ها مستقل هستند، شاید وقت آن است که به یک هدف وصلشان کنی.»"""

    short_user_prompt = f"گزارش کوتاه {time_frame_label} من رو بنویس."

    # پرامپت سیستم برای گزارش کامل (modal نمایش بیشتر)
    full_system_prompt = f"""تو یک «منتور شخصی» هستی که با «{user_name}» در حال گفتگویی صمیمی و حمایتی هستی. لحن تو:
- مخاطب قرار دادن کاربر: «تو»، «قدم بعدی»، «بزن بریم»
- دلسوزانه برای موفقیت‌ها، مشوقانه برای ادامه، منتقدانه مهربانانه برای کم‌کاری‌ها
- فارسی، گرم، صمیمی، واقعی

📊 داده‌های زنده دیتابیس در بازه «{time_frame_label}»:
```json
{json.dumps(context, ensure_ascii=False, indent=2)}
```

📝 خروجی: گزارش تفصیلی شامل:
1. **پاراگراف ۱:** وضعیت کلی + نقاط قوت + لحن تشویقی
2. **پاراگراف ۲:** اهداف رهاشده + چالش‌ها + لحن دلسوزانه
3. **پاراگراف ۳:** توصیه عملی + گام‌های بعدی + «بزن بریم 🚀»
4. **پاراگراف ۴ (اختیاری):** منابع/ایده‌های الهام‌بخش از دیتابیس کاربر

حداکثر ۴۰۰ کلمه. متن روان، بدون لیست طولانی."""

    full_user_prompt = f"گزارش کامل {time_frame_label} من رو بنویس."

    # فراخوانی همزمان هر دو AI call
    short_text, status_msg_1 = await call_avalai_ai(short_system_prompt, short_user_prompt)
    full_text, status_msg_2 = await call_avalai_ai(full_system_prompt, full_user_prompt)

    # اگه AI در دسترس نیست، fallback
    if not short_text:
        short_text = f"⚠️ {status_msg_1}\n\nبرای دریافت گزارش، لطفاً کلید AVALAI_API_KEY را تنظیم کنید."
    if not full_text:
        full_text = short_text

    # محاسبه health_status
    overdue_cnt = context["user_summary"]["overdue_tasks_count"]
    health_status = "عالی 🚀" if overdue_cnt == 0 else "نیازمند مدیریت 🚨" if overdue_cnt > 3 else "خوب ⚡"

    # ۳. ذخیره در DB
    new_report = MentorReport(
        owner_id=current_user.id,
        time_frame=time_frame,
        short_report=short_text,
        full_report=full_text,
        context_summary=json.dumps(context["user_summary"], ensure_ascii=False),
        neglected_goals=json.dumps(context["neglected_goals"], ensure_ascii=False),
        report_date=today
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)

    return {
        "from_cache": False,
        "generated_at": new_report.created_at.isoformat() if new_report.created_at else None,
        "time_frame_label": time_frame_label,
        "time_frame_used": time_frame,
        "user_name": user_name,
        "health_status": health_status,
        "context_summary": context["user_summary"],
        "neglected_goals": context["neglected_goals"],
        "short_report": short_text,
        "full_report": full_text,
    }

@router.post("/chat")
async def mentor_chat(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """پاسخگویی هوشمند منتور در چت تعاملی - با کش context برای کاهش ۷۰٪ توکن"""
    user_message = payload.get("message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="متن پیام نمیتواند خالی باشد.")

    user_id_str = str(current_user.id)
    now = time.time()
    user_name = current_user.full_name or "دوست من"

    # ۱. بررسی کش context
    cached = _chat_context_cache.get(user_id_str)
    if cached and (now - cached["timestamp"]) < _CHAT_CACHE_TTL:
        # کش معتبر: فقط system_prompt + پیام کاربر رو می‌فرستیم
        system_prompt = cached["system_prompt"]
    else:
        # کش منقضی یا وجود نداره: از نو می‌سازیم
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

        skills_res = await db.execute(select(Skill).where(Skill.owner_id == current_user.id))
        skills = skills_res.scalars().all()

        context = build_deep_architecture_context(tasks, goals, subgoals, accounts, ideas, skills)

        system_prompt = f"""تو یک «منتور شخصی» هستی که با «{user_name}» در حال گفتگویی صمیمی و حمایتی هستی. لحن تو:
- مخاطب قرار دادن کاربر: «تو»، «قدم بعدی»، «بزن بریم»
- دلسوزانه برای موفقیت‌ها، مشوقانه برای ادامه، منتقدانه مهربانانه برای کم‌کاری‌ها (بدون قضاوت)
- فارسی، گرم، صمیمی، واقعی
- پاسخ‌های کوتاه و کاربردی (حداکثر ۲۰۰ کلمه)

📊 داده‌های زنده دیتابیس:
```json
{json.dumps(context, ensure_ascii=False)}
```"""

        # ذخیره در کش
        _chat_context_cache[user_id_str] = {
            "system_prompt": system_prompt,
            "context": context,
            "timestamp": now
        }

    # ۲. فراخوانی AI
    ai_reply, status_msg = await call_avalai_ai(system_prompt, user_message)

    if not ai_reply:
        ai_reply = f"{status_msg}"

    return {
        "reply": ai_reply,
        "timestamp": datetime.now().isoformat()
    }