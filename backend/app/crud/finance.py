from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.all_models import Account, Transaction
from app.schemas.finance import AccountCreate, AccountUpdate, TransactionCreate
from datetime import date

# --- بخش حساب‌ها ---
async def get_accounts(db: AsyncSession, owner_id: int):
    result = await db.execute(
        select(Account).where(Account.owner_id == owner_id).options(selectinload(Account.transactions)).order_by(Account.created_at.desc())
    )
    accounts = result.scalars().all()
    for acc in accounts:
        acc.transaction_count = len(acc.transactions)
        acc.total_deposits = sum(t.amount for t in acc.transactions if t.transaction_type == 'deposit')
        acc.total_withdrawals = sum(t.amount for t in acc.transactions if t.transaction_type == 'withdrawal')
    return accounts

async def get_account(db: AsyncSession, account_id: int, owner_id: int):
    result = await db.execute(select(Account).where(Account.id == account_id, Account.owner_id == owner_id))
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

# --- بخش تراکنش‌ها ---
async def create_transaction(db: AsyncSession, account_id: int, trans: TransactionCreate, owner_id: int):
    acc_result = await db.execute(select(Account).where(Account.id == account_id, Account.owner_id == owner_id))
    account = acc_result.scalar_one_or_none()
    if not account: return None
    
    amount_change = trans.amount if trans.transaction_type == 'deposit' else -trans.amount
    new_balance = account.current_balance + amount_change
    
    # اصلاح تداخل فیلدها:
    data = trans.model_dump()
    data.pop('balance_after', None) # اگر در دیتا بود حذفش کن تا تداخل نخوریم
    
    db_trans = Transaction(
        **data,
        account_id=account_id,
        owner_id=owner_id,
        balance_after=new_balance
    )
    
    db.add(db_trans)
    account.current_balance = new_balance
    await db.commit(); await db.refresh(db_trans)
    return db_trans

async def get_transactions(db: AsyncSession, account_id: int, owner_id: int):
    result = await db.execute(
        select(Transaction).where(Transaction.account_id == account_id, Transaction.owner_id == owner_id).order_by(Transaction.id.desc())
    )
    return result.scalars().all()

async def delete_transaction(db: AsyncSession, trans_id: int, owner_id: int):
    result = await db.execute(select(Transaction).where(Transaction.id == trans_id, Transaction.owner_id == owner_id))
    db_trans = result.scalar_one_or_none()
    if not db_trans: return None

    account_result = await db.execute(select(Account).where(Account.id == db_trans.account_id))
    account = account_result.scalar_one_or_none()
    
    delta = -db_trans.amount if db_trans.transaction_type == 'deposit' else db_trans.amount
    
    # اصلاح تراکنش‌های بعدی
    sub_res = await db.execute(select(Transaction).where(and_(Transaction.account_id == db_trans.account_id, Transaction.id > db_trans.id)))
    for t in sub_res.scalars().all(): t.balance_after += delta
    
    if account: account.current_balance += delta
    
    await db.delete(db_trans); await db.commit()
    return {"message": "deleted"}

async def update_transaction(db: AsyncSession, trans_id: int, owner_id: int, trans_update: TransactionCreate):
    result = await db.execute(select(Transaction).where(Transaction.id == trans_id, Transaction.owner_id == owner_id))
    db_trans = result.scalar_one_or_none()
    if not db_trans: return None

    account_result = await db.execute(select(Account).where(Account.id == db_trans.account_id))
    account = account_result.scalar_one_or_none()

    old_impact = db_trans.amount if db_trans.transaction_type == 'deposit' else -db_trans.amount
    new_impact = trans_update.amount if trans_update.transaction_type == 'deposit' else -trans_update.amount
    delta = new_impact - old_impact

    # بروزرسانی داده‌ها
    for k, v in trans_update.model_dump().items():
        if k != 'balance_after': setattr(db_trans, k, v)
    db_trans.balance_after += delta

    sub_res = await db.execute(select(Transaction).where(and_(Transaction.account_id == db_trans.account_id, Transaction.id > db_trans.id)))
    for t in sub_res.scalars().all(): t.balance_after += delta

    if account: account.current_balance += delta
    await db.commit(); await db.refresh(db_trans)
    return db_trans