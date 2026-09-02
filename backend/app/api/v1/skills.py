from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from datetime import date, timedelta
from typing import Optional
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Skill, LearningLog, Goal
from app.schemas.skill import (
    SkillCreate, SkillUpdate, SkillResponse, SkillStats,
    LearningLogCreate, LearningLogResponse
)
from app.crud import skill as crud_skill

router = APIRouter()

@router.get("/", response_model=list[SkillResponse])
async def list_skills(
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    goal_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """لیست مهارت‌ها با فیلتر پیشرفته"""
    q = (
        select(Skill)
        .options(selectinload(Skill.learning_logs))
        .where(Skill.owner_id == current_user.id)
    )
    if category:
        q = q.where(Skill.category == category)
    if status_filter:
        q = q.where(Skill.status == status_filter)
    if goal_id is not None:
        if goal_id == -1:  # -1 = مهارت‌های مستقل (بدون هدف)
            q = q.where(Skill.goal_id.is_(None))
        else:
            q = q.where(Skill.goal_id == goal_id)
    if search:
        q = q.where(Skill.title.contains(search))
    q = q.order_by(desc(Skill.id))
    res = await db.execute(q)
    skills = res.scalars().all()

    # اضافه کردن goal_title
    goal_ids = [s.goal_id for s in skills if s.goal_id]
    goal_titles = {}
    if goal_ids:
        gq = await db.execute(select(Goal.id, Goal.title).where(Goal.id.in_(goal_ids)))
        goal_titles = {g[0]: g[1] for g in gq.all()}

    result = []
    for s in skills:
        resp = SkillResponse.model_validate(s)
        if s.goal_id and s.goal_id in goal_titles:
            resp.goal_title = goal_titles[s.goal_id]
        result.append(resp)
    return result

@router.post("/", response_model=SkillResponse)
async def create_skill(data: SkillCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await crud_skill.create_skill(db, current_user.id, data)
    return s

@router.get("/by_id/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(Skill).options(selectinload(Skill.learning_logs)).where(Skill.id == skill_id, Skill.owner_id == current_user.id)
    res = await db.execute(q)
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="مهارت یافت نشد")
    return s

@router.put("/by_id/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: int, data: SkillUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await crud_skill.update_skill(db, current_user.id, skill_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="مهارت یافت نشد")
    return s

@router.delete("/by_id/{skill_id}")
async def delete_skill(skill_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(Skill).where(Skill.id == skill_id, Skill.owner_id == current_user.id)
    res = await db.execute(q)
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="مهارت یافت نشد")
    await db.delete(s)
    await db.commit()
    return {"ok": True, "message": "مهارت حذف شد"}

@router.get("/_stats/summary", response_model=SkillStats)
async def get_skill_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """آمار کلی مهارت‌ها شامل streak"""
    # دریافت همه مهارت‌ها
    skills_q = await db.execute(select(Skill).where(Skill.owner_id == current_user.id))
    skills = skills_q.scalars().all()

    # دریافت همه log ها (برای streak)
    logs_q = await db.execute(
        select(LearningLog)
        .where(LearningLog.owner_id == current_user.id)
        .order_by(desc(LearningLog.log_date))
    )
    logs = logs_q.scalars().all()

    # محاسبه streak: روزهای متوالی که حداقل یک log داشتی
    log_dates = sorted({l.log_date for l in logs}, reverse=True)
    today = date.today()
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    if log_dates:
        # Current streak
        check_date = today
        for ld in log_dates:
            if ld == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif ld < check_date:
                break

        # Longest streak
        sorted_asc = sorted(log_dates)
        temp_streak = 1
        longest_streak = 1
        for i in range(1, len(sorted_asc)):
            if (sorted_asc[i] - sorted_asc[i-1]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1

    # آمار
    total = len(skills)
    mastered = sum(1 for s in skills if s.status == 'mastered')
    in_progress = sum(1 for s in skills if s.status == 'in_progress')
    on_hold = sum(1 for s in skills if s.status == 'on_hold')
    independent = sum(1 for s in skills if s.goal_id is None)
    avg_progress = sum(s.progress_percent for s in skills) / total if total > 0 else 0
    total_hours = sum(s.practiced_hours or 0 for s in skills)

    # دسته‌بندی
    by_category = {}
    for s in skills:
        cat = s.category or 'عمومی'
        by_category[cat] = by_category.get(cat, 0) + 1

    # فعالیت ۳۰ روز اخیر
    thirty_days_ago = today - timedelta(days=30)
    recent = sum(1 for l in logs if l.log_date >= thirty_days_ago)

    return SkillStats(
        total_skills=total,
        mastered=mastered,
        in_progress=in_progress,
        on_hold=on_hold,
        independent_skills=independent,
        overall_progress_avg=round(avg_progress, 1),
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_practiced_hours=round(total_hours, 1),
        by_category=by_category,
        recent_activity_30days=recent
    )


@router.get("/_logs", response_model=list[LearningLogResponse])
async def list_learning_logs(
    skill_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """لیست log های یادگیری با فیلتر"""
    q = select(LearningLog).where(LearningLog.owner_id == current_user.id)
    if skill_id:
        q = q.where(LearningLog.skill_id == skill_id)
    if search:
        q = q.where(LearningLog.title.contains(search) | LearningLog.content.contains(search))
    q = q.order_by(desc(LearningLog.log_date)).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

@router.post("/_logs", response_model=LearningLogResponse)
async def create_learning_log(data: LearningLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    log = await crud_skill.create_learning_log(db, current_user.id, data)
    # به‌روزرسانی last_practiced مهارت مرتبط
    if data.skill_id:
        sq = select(Skill).where(Skill.id == data.skill_id, Skill.owner_id == current_user.id)
        sr = await db.execute(sq)
        skill = sr.scalar_one_or_none()
        if skill:
            skill.last_practiced = data.log_date
            if data.duration_minutes:
                skill.practiced_hours = (skill.practiced_hours or 0) + (data.duration_minutes / 60)
            await db.commit()
    return log

@router.delete("/_logs/{log_id}")
async def delete_learning_log(log_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = select(LearningLog).where(LearningLog.id == log_id, LearningLog.owner_id == current_user.id)
    res = await db.execute(q)
    log = res.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="لاگ یافت نشد")
    await db.delete(log)
    await db.commit()
    return {"ok": True}