from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.movie import MovieCreate, MovieUpdate, MovieRead
from app.crud import movie as movie_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/", response_model=List[MovieRead])
async def get_movies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await movie_crud.get_movies(db, current_user.id)

@router.post("/", response_model=MovieRead)
async def create_movie(
    data: MovieCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await movie_crud.create_movie(db, data, current_user.id)

@router.put("/{movie_id}", response_model=MovieRead)
async def update_movie(
    movie_id: int,
    data: MovieUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await movie_crud.update_movie(db, movie_id, current_user.id, data)
    if not result: raise HTTPException(404, "Movie not found")
    return result

@router.delete("/{movie_id}")
async def delete_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await movie_crud.delete_movie(db, movie_id, current_user.id)
    if not result: raise HTTPException(404, "Movie not found")
    return {"message": "deleted"}

@router.get("/categories")
async def get_categories():
    return [
        {"value": "action", "label": "اکشن"},
        {"value": "comedy", "label": "کمدی"},
        {"value": "drama", "label": "درام"},
        {"value": "horror", "label": "ترسناک"},
        {"value": "sci-fi", "label": "علمی تخیلی"},
        {"value": "animation", "label": "انیمیشن"},
        {"value": "documentary", "label": "مستند"},
        {"value": "romance", "label": "عاشقانه"},
        {"value": "other", "label": "سایر"},
    ]