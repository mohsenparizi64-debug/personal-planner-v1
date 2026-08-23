from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import Place
from app.schemas.place import PlaceCreate, PlaceUpdate
from datetime import date

async def get_places(db: AsyncSession, owner_id: int):
    result = await db.execute(
        select(Place).where(Place.owner_id == owner_id).order_by(Place.is_favorite.desc(), Place.created_at.desc())
    )
    return list(result.scalars().all())

async def get_place(db: AsyncSession, place_id: int, owner_id: int):
    result = await db.execute(select(Place).where(Place.id == place_id, Place.owner_id == owner_id))
    return result.scalar_one_or_none()

async def create_place(db: AsyncSession, place: PlaceCreate, owner_id: int):
    db_place = Place(**place.model_dump(), owner_id=owner_id)
    if not db_place.register_date: db_place.register_date = date.today()
    db.add(db_place); await db.commit(); await db.refresh(db_place)
    return db_place

async def update_place(db: AsyncSession, place_id: int, owner_id: int, update: PlaceUpdate):
    db_place = await get_place(db, place_id, owner_id)
    if not db_place: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_place, k, v)
    await db.commit(); await db.refresh(db_place)
    return db_place

async def delete_place(db: AsyncSession, place_id: int, owner_id: int):
    db_place = await get_place(db, place_id, owner_id)
    if not db_place: return None
    await db.delete(db_place); await db.commit()
    return db_place