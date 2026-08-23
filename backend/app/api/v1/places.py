from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.place import PlaceCreate, PlaceUpdate, PlaceRead
from app.crud import place as place_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/", response_model=List[PlaceRead])
async def get_places(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await place_crud.get_places(db, current_user.id)

@router.post("/", response_model=PlaceRead)
async def create_place(
    data: PlaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await place_crud.create_place(db, data, current_user.id)

@router.put("/{place_id}", response_model=PlaceRead)
async def update_place(
    place_id: int,
    data: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await place_crud.update_place(db, place_id, current_user.id, data)
    if not result: raise HTTPException(404, "Place not found")
    return result

@router.delete("/{place_id}")
async def delete_place(
    place_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await place_crud.delete_place(db, place_id, current_user.id)
    if not result: raise HTTPException(404, "Place not found")
    return {"message": "deleted"}

@router.get("/categories")
async def get_categories():
    return [
        {"value": "restaurant", "label": "رستوران و کافه", "icon": "🍽️"},
        {"value": "nature", "label": "طبیعت و پارک", "icon": "🌿"},
        {"value": "historical", "label": "تاریخی و فرهنگی", "icon": "🏛️"},
        {"value": "shopping", "label": "خرید", "icon": "🛍️"},
        {"value": "service", "label": "خدمات", "icon": "🏪"},
        {"value": "entertainment", "label": "تفریحی", "icon": "🎢"},
        {"value": "sport", "label": "ورزشی", "icon": "⚽"},
        {"value": "other", "label": "سایر", "icon": "📍"},
    ]