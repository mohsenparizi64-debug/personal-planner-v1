from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.book import BookCreate, BookUpdate, BookRead
from app.crud import book as book_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

@router.get("/", response_model=List[BookRead])
async def get_books(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await book_crud.get_books(db, current_user.id)

@router.post("/", response_model=BookRead)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await book_crud.create_book(db, data, current_user.id)

@router.put("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await book_crud.update_book(db, book_id, current_user.id, data)
    if not result: raise HTTPException(404, "Book not found")
    return result

@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await book_crud.delete_book(db, book_id, current_user.id)
    if not result: raise HTTPException(404, "Book not found")
    return {"message": "deleted"}

@router.get("/categories")
async def get_categories():
    return [
        {"value": "novel", "label": "رمان"},
        {"value": "science", "label": "علمی"},
        {"value": "history", "label": "تاریخی"},
        {"value": "philosophy", "label": "فلسفه"},
        {"value": "psychology", "label": "روانشناسی"},
        {"value": "business", "label": "کسب‌وکار"},
        {"value": "poetry", "label": "شعر"},
        {"value": "biography", "label": "زندگی‌نامه"},
        {"value": "other", "label": "سایر"},
    ]