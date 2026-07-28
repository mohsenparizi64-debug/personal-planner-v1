from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.all_models import User
from app.core.security import get_password_hash, verify_password
from datetime import datetime

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, email: str, password: str, full_name: str = None, phone: str = None):
    hashed = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed, full_name=full_name, phone=phone)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, update_data: dict):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    for k, v in update_data.items():
        if v is not None:
            setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def generate_password_reset_token(db: AsyncSession, email: str):
    from app.core.security import generate_reset_token, get_reset_token_expiry
    user = await get_user_by_email(db, email)
    if not user: return None
    user.reset_token = generate_reset_token()
    user.reset_token_expires = get_reset_token_expiry()
    await db.commit()
    return user.reset_token

async def get_user_by_reset_token(db: AsyncSession, token: str):
    result = await db.execute(select(User).where(User.reset_token == token, User.reset_token_expires > datetime.utcnow()))
    return result.scalar_one_or_none()

async def reset_password(db: AsyncSession, token: str, new_password: str):
    user = await get_user_by_reset_token(db, token)
    if not user: return False
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
    return True