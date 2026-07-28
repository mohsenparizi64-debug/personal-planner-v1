from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.all_models import Account, Transaction
from app.schemas.finance import AccountCreate, AccountUpdate, TransactionCreate
from datetime import date

async def get_accounts(db: AsyncSession, owner_id: int):
    result = await db.execute(select(Account).where(Account.owner_id == owner_id).options(selectinload(Account.transactions)).order_by(Account.created_at.desc()))
    accounts = result.scalars().all()
    for acc in accounts:
        acc.transaction_count = len(acc.transactions)
        acc.total_deposits = sum(t.amount for t in acc.transactions if t.transaction_type == 'deposit')
        acc.total_withdrawals = sum(t.amount for t in acc.transactions if t.transaction_type == 'withdrawal')
    return accounts

async def get_account(db: AsyncSession, account_id: int, owner_id: int):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.owner_id == owner_id).options(selectinload(Account.transactions)))
    return result.scalar_one_or_none()

async def create_account(db: AsyncSession, account: AccountCreate, owner_id: int):
    db_acc = Account(**account.model_dump(), owner_id=owner_id)
    if not db_acc.register_date: db_acc.register_date = date.today()
    db.add(db_acc); await db.commit(); await db.refresh(db_acc)
    return db_acc

async def update_account(db: AsyncSession, account_id: int, owner_id: int, update: AccountUpdate):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.owner_id == owner_id))
    db_acc = result.scalar_one_or_none()
    if not db_acc: return None
    for k, v in update.model_dump(exclude_unset=True).items(): setattr(db_acc, k, v)
    await db.commit(); await db.refresh(db_acc)
    return db_acc

async def delete_account(db: AsyncSession, account_id: int, owner_id: int):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.owner_id == owner_id))
    db_acc = result.scalar_one_or_none()
    if not db_acc: return None
    await db.delete(db_acc); await db.commit()
    return db_acc

async def create_transaction(db: AsyncSession, account_id: int, trans: TransactionCreate, owner_id: int):
    account = await get_account(db, account_id, owner_id)
    if not account: return None
    balance_after = account.current_balance + trans.amount if trans.transaction_type == 'deposit' else account.current_balance - trans.amount
    trans_data = trans.model_dump()
    trans_data.pop('balance_after', None)
    db_trans = Transaction(**trans_data, account_id=account_id, owner_id=owner_id, balance_after=balance_after)
    db.add(db_trans)
    account.current_balance = balance_after
    await db.commit(); await db.refresh(db_trans)
    return db_trans

async def get_transactions(db: AsyncSession, account_id: int, owner_id: int):
    result = await db.execute(select(Transaction).where(Transaction.account_id == account_id, Transaction.owner_id == owner_id).order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()))
    return result.scalars().all()

async def delete_transaction(db: AsyncSession, trans_id: int, owner_id: int):
    result = await db.execute(select(Transaction).where(Transaction.id == trans_id, Transaction.owner_id == owner_id))
    db_trans = result.scalar_one_or_none()
    if not db_trans: return None
    account = await get_account(db, db_trans.account_id, owner_id)
    if account:
        if db_trans.transaction_type == 'deposit': account.current_balance -= db_trans.amount
        else: account.current_balance += db_trans.amount
    await db.delete(db_trans); await db.commit()
    return db_trans