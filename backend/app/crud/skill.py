from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.all_models import Skill, LearningLog
from app.schemas.skill import SkillCreate, SkillUpdate, LearningLogCreate

async def get_skills(db: AsyncSession, user_id: int, limit: int = 5000):
    q = (
        select(Skill)
        .options(selectinload(Skill.learning_logs))  # جلوگیری از لود تنبل همزمان
        .where(Skill.owner_id == user_id)
        .order_by(desc(Skill.id))
        .limit(limit)
    )
    res = await db.execute(q)
    return res.scalars().all()

async def create_skill(db: AsyncSession, user_id: int, data: SkillCreate):
    s = Skill(**data.model_dump(), owner_id=user_id)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    # لود eager برای learning_logs (جلوگیری از lazy load که در async مشکل ایجاد می‌کنه)
    q = select(Skill).options(selectinload(Skill.learning_logs)).where(Skill.id == s.id)
    res = await db.execute(q)
    return res.scalar_one()

async def update_skill(db: AsyncSession, user_id: int, skill_id: int, data: SkillUpdate):
    q = select(Skill).where(Skill.id == skill_id, Skill.owner_id == user_id)
    res = await db.execute(q)
    s = res.scalar_one_or_none()
    if s:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(s, k, v)
        await db.commit()
        # بارگذاری مجدد با eager load
        q2 = select(Skill).options(selectinload(Skill.learning_logs)).where(Skill.id == skill_id)
        res2 = await db.execute(q2)
        return res2.scalar_one()
    return s

async def get_learning_logs(db: AsyncSession, user_id: int, limit: int = 5000):
    q = select(LearningLog).where(LearningLog.owner_id == user_id).order_by(desc(LearningLog.log_date)).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

async def create_learning_log(db: AsyncSession, user_id: int, data: LearningLogCreate):
    log = LearningLog(**data.model_dump(), owner_id=user_id)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log