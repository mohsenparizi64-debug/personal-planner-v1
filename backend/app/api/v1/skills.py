from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User
from app.schemas.skill import (
    SkillCreate, SkillUpdate, SkillResponse,
    LearningLogCreate, LearningLogResponse
)
from app.crud import skill as crud_skill

router = APIRouter()

@router.get("/", response_model=list[SkillResponse])
async def list_skills(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_skill.get_skills(db, current_user.id)

@router.post("/", response_model=SkillResponse)
async def create_skill(data: SkillCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_skill.create_skill(db, current_user.id, data)

@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: int, data: SkillUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await crud_skill.update_skill(db, current_user.id, skill_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="Skill not found")
    return s

@router.get("/logs", response_model=list[LearningLogResponse])
async def list_learning_logs(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_skill.get_learning_logs(db, current_user.id)

@router.post("/logs", response_model=LearningLogResponse)
async def create_learning_log(data: LearningLogCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud_skill.create_learning_log(db, current_user.id, data)