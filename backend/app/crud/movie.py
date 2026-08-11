from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import Movie
from app.schemas.movie import MovieCreate, MovieUpdate
from datetime import datetime

# تابع کمکی برای تبدیل امن تاریخ‌ها به None در صورت خالی بودن
def _clean_date_fields(data: dict):
    for field in ["watch_date", "register_date"]:
        if field in data and (data[field] == "" or data[field] is None):
            data[field] = None
        elif field in data and isinstance(data[field], str) and data[field].strip():
            try:
                # تبدیل رشته YYYY-MM-DD به date پایتون برای دیتابیس
                data[field] = datetime.strptime(data[field].split("T")[0], "%Y-%m-%d").date()
            except Exception:
                data[field] = None
    return data

async def get_movies(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Movie).where(Movie.owner_id == owner_id).order_by(Movie.id.desc()))
    return result.scalars().all()

async def create_movie(db: AsyncSession, movie: MovieCreate, owner_id: int):
    data = _clean_date_fields(movie.model_dump())
    db_movie = Movie(**data, owner_id=owner_id)
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie)
    return db_movie

async def update_movie(db: AsyncSession, movie_id: int, owner_id: int, update: MovieUpdate):
    result = await db.execute(select(Movie).where(Movie.id == movie_id, Movie.owner_id == owner_id))
    db_movie = result.scalar_one_or_none()
    if db_movie:
        data = _clean_date_fields(update.model_dump(exclude_unset=True))
        for k, v in data.items():
            setattr(db_movie, k, v)
        await db.commit()
        await db.refresh(db_movie)
    return db_movie

async def delete_movie(db: AsyncSession, movie_id: int, owner_id: int):
    result = await db.execute(select(Movie).where(Movie.id == movie_id, Movie.owner_id == owner_id))
    db_movie = result.scalar_one_or_none()
    if db_movie:
        await db.delete(db_movie)
        await db.commit()
        return True
    return False