from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.finance import AccountCreate, AccountUpdate, TransactionCreate, TransactionRead
from app.crud import finance as finance_crud
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User

router = APIRouter()

# --- مسیرهای حساب ---
@router.get("/accounts")
async def get_accounts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await finance_crud.get_accounts(db, current_user.id)

@router.post("/accounts")
async def create_account(data: AccountCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await finance_crud.create_account(db, data, current_user.id)

@router.put("/accounts/{account_id}")
async def update_account(account_id: int, data: AccountUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await finance_crud.update_account(db, account_id, current_user.id, data)
    if not result: raise HTTPException(404, "Account not found")
    return result

@router.delete("/accounts/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await finance_crud.delete_account(db, account_id, current_user.id)
    if not result: raise HTTPException(404, "Account not found")
    return {"message": "deleted"}

# --- مسیرهای تراکنش ---
@router.get("/accounts/{account_id}/transactions", response_model=List[TransactionRead])
async def get_transactions(account_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await finance_crud.get_transactions(db, account_id, current_user.id)

@router.post("/accounts/{account_id}/transactions", response_model=TransactionRead)
async def create_transaction(account_id: int, data: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await finance_crud.create_transaction(db, account_id, data, current_user.id)
    if not result: raise HTTPException(404, "Account not found")
    return result

# اضافه کردن مسیر ویرایش تراکنش
@router.put("/transactions/{trans_id}", response_model=TransactionRead)
async def update_transaction(trans_id: int, data: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await finance_crud.update_transaction(db, trans_id, current_user.id, data)
    if not result: raise HTTPException(404, "Transaction not found")
    return result

@router.delete("/transactions/{trans_id}")
async def delete_transaction(trans_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await finance_crud.delete_transaction(db, trans_id, current_user.id)
    if not result: raise HTTPException(404, "Transaction not found")
    return {"message": "deleted"}