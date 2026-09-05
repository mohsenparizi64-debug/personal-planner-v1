from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import Goal, GoalLog
from app.schemas.goal import GoalCreate, GoalUpdate

async def create_goal_log(db: AsyncSession, goal_id: int, owner_id: int, action: str, field_name: str = None, old_value: str = None, new_value: str = None, description: str = None):
    log = GoalLog(goal_id=goal_id, owner_id=owner_id, action=action, field_name=field_name, old_value=old_value, new_value=new_value, description=description)
    db.add(log)
    await db.commit()

async def get_goal_logs(db: AsyncSession, owner_id: int, limit: int = 20):
    result = await db.execute(select(GoalLog).where(GoalLog.owner_id == owner_id).order_by(GoalLog.created_at.desc()).limit(limit))
    logs = result.scalars().all()
    # تبدیل صریح به dict برای جلوگیری از ResponseValidationError هنگام NULL
    out = []
    for log in logs:
        out.append({
            "id": log.id,
            "goal_id": log.goal_id if log.goal_id is not None else 0,
            "action": log.action or "",
            "field_name": log.field_name,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "description": log.description,
            "owner_id": log.owner_id,
            "created_at": log.created_at,
        })
    return out

async def get_goal_logs_by_goal(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(select(GoalLog).where(GoalLog.goal_id == goal_id, GoalLog.owner_id == owner_id).order_by(GoalLog.created_at.desc()))
    return result.scalars().all()

async def get_goals(db: AsyncSession, owner_id: int, skip: int = 0, limit: int = 50):
    result = await db.execute(select(Goal).where(Goal.owner_id == owner_id).order_by(Goal.priority.desc(), Goal.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def get_goal(db: AsyncSession, goal_id: int, owner_id: int):
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.owner_id == owner_id))
    return result.scalar_one_or_none()

async def create_goal(db: AsyncSession, goal: GoalCreate, owner_id: int):
    db_goal = Goal(**goal.model_dump(), owner_id=owner_id)
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    await create_goal_log(db, db_goal.id, owner_id, action="created", description=f"هدف '{goal.title}' ایجاد شد")
    return db_goal

async def update_goal(db: AsyncSession, goal_id: int, owner_id: int, goal_update: GoalUpdate):
    db_goal = await get_goal(db, goal_id, owner_id)
    if not db_goal:
        return None
    update_data = goal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(db_goal, key, None)
        if str(old_value) != str(value):
            field_labels = {'title': 'عنوان', 'description': 'توضیحات', 'start_date': 'تاریخ شروع', 'target_date': 'تاریخ هدف', 'current_status': 'آخرین وضعیت', 'current_obstacle': 'مانع فعلی', 'next_step': 'گام بعدی', 'priority': 'اولویت', 'success_criteria': 'معیار موفقیت'}
            field_label = field_labels.get(key, key)
            await create_goal_log(db, goal_id, owner_id, action="updated", field_name=field_label, old_value=str(old_value) if old_value else "خالی", new_value=str(value), description=f"'{field_label}' از '{old_value}' به '{value}' تغییر کرد")
        setattr(db_goal, key, value)
    await db.commit()
    await db.refresh(db_goal)
    return db_goal

async def delete_goal(db: AsyncSession, goal_id: int, owner_id: int):
    db_goal = await get_goal(db, goal_id, owner_id)
    if not db_goal:
        return None
    await create_goal_log(db, goal_id, owner_id, action="deleted", description=f"هدف '{db_goal.title}' حذف شد")
    await db.delete(db_goal)
    await db.commit()
    return db_goal

async def delete_all_goals(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Goal).where(Goal.owner_id == owner_id))
    goals = result.scalars().all()
    count = len(goals)
    for goal in goals:
        await db.delete(goal)
    await db.commit()
    return count