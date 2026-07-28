from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import Movie
from app.schemas.movie import MovieCreate, MovieUpdate
from datetime import date

async def get_movies(db: AsyncSession, owner_id: int):
    result = await db.execute(
        select(Movie)
        .where(Movie.owner_id == owner_id)
        .order_by(Movie.created_at.desc())
    )
    return list(result.scalars().all())

async def get_movie(db: AsyncSession, movie_id: int, owner_id: int):
    result = await db.execute(
        select(Movie).where(Movie.id == movie_id, Movie.owner_id == owner_id)
    )
    return result.scalar_one_or_none()

async def create_movie(db: AsyncSession, movie: MovieCreate, owner_id: int):
    db_movie = Movie(**movie.model_dump(), owner_id=owner_id)
    if not db_movie.register_date:
        db_movie.register_date = date.today()
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie)
    return db_movie

async def update_movie(db: AsyncSession, movie_id: int, owner_id: int, update: MovieUpdate):
    db_movie = await get_movie(db, movie_id, owner_id)
    if not db_movie:
        return None
    for k, v in update.model_dump(exclude_unset=True).items():
        setattr(db_movie, k, v)
    await db.commit()
    await db.refresh(db_movie)
    return db_movie

async def delete_movie(db: AsyncSession, movie_id: int, owner_id: int):
    db_movie = await get_movie(db, movie_id, owner_id)
    if not db_movie:
        return None
    await db.delete(db_movie)
    await db.commit()
    return db_movie