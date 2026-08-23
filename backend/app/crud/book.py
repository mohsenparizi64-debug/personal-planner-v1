from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import Book
from app.schemas.book import BookCreate, BookUpdate
from datetime import date

async def get_books(db: AsyncSession, owner_id: int):
    result = await db.execute(
        select(Book).where(Book.owner_id == owner_id).order_by(Book.created_at.desc())
    )
    return list(result.scalars().all())

async def get_book(db: AsyncSession, book_id: int, owner_id: int):
    result = await db.execute(select(Book).where(Book.id == book_id, Book.owner_id == owner_id))
    return result.scalar_one_or_none()

async def create_book(db: AsyncSession, book: BookCreate, owner_id: int):
    db_book = Book(**book.model_dump(), owner_id=owner_id)
    if not db_book.register_date: db_book.register_date = date.today()
    db.add(db_book); await db.commit(); await db.refresh(db_book)
    return db_book

async def update_book(db: AsyncSession, book_id: int, owner_id: int, update: BookUpdate):
    db_book = await get_book(db, book_id, owner_id)
    if not db_book: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_book, k, v)
    await db.commit(); await db.refresh(db_book)
    return db_book

async def delete_book(db: AsyncSession, book_id: int, owner_id: int):
    db_book = await get_book(db, book_id, owner_id)
    if not db_book: return None
    await db.delete(db_book); await db.commit()
    return db_book