from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models.all_models import Account, Transaction
from app.schemas.finance import AccountCreate, AccountUpdate, TransactionCreate
from datetime import date, datetime, timedelta
from collections import OrderedDict

# --- نگاشت نام روز هفته میلادی به فارسی (شنبه = 0) ---
_WEEKDAY_FROM_SAT = {
    5: "شنبه",   # Sat
    6: "یکشنبه", # Sun
    0: "دوشنبه", # Mon
    1: "سه‌شنبه", # Tue
    2: "چهارشنبه", # Wed
    3: "پنج‌شنبه", # Thu
    4: "جمعه",   # Fri
}

def _parse_transaction_date(raw):
    """تبدیل transaction_date (رشته YYYY-MM-DD) به datetime؛ None در صورت نامعتبر"""
    if not raw:
        return None
    try:
        s = str(raw)[:10]
        return datetime.strptime(s, '%Y-%m-%d')
    except Exception:
        return None

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


# ====== گزارش چند-بازه‌ای برای صفحه مالی ======
async def get_recent_finance_report(db: AsyncSession, owner_id: int, days: int = 7, account_ids: list | None = None):
    """
    گزارش تراکنش‌های بازه اخیر.
    days فقط 7/30/90 — در غیر این صورت 7.
    account_ids: لیست id حساب‌های داخل تحلیل؛ None یعنی همه حساب‌های غیرمخفی.
    حساب مخفی (is_hidden) همیشه از جمع‌ها بیرون است مگر صراحتاً انتخاب شود.
    باکت‌بندی: 7 و 30 روزانه؛ 90 هفتگی (شنبه تا جمعه).
    خروجی: summary + buckets + category_breakdown + account_breakdown
    """
    if days not in (7, 30, 90):
        days = 7

    today = datetime.utcnow().date()
    days_since_saturday = (today.weekday() - 5) % 7
    start_date = today - timedelta(days=days_since_saturday)

    acc_res = await db.execute(select(Account.id, Account.is_hidden).where(Account.owner_id == owner_id))
    hidden_ids = {row[0] for row in acc_res.all() if row[1]}
    owned_ids = {row[0] for row in (await db.execute(select(Account.id).where(Account.owner_id == owner_id))).all()}

    if account_ids:
        scope_ids = {i for i in account_ids if i in owned_ids}
    else:
        scope_ids = owned_ids - hidden_ids

    res = await db.execute(
        select(Transaction).where(
            Transaction.owner_id == owner_id
        ).order_by(Transaction.id.asc())
    )
    all_tx = res.scalars().all()

    bucket_kind = "week" if days == 90 else "day"
    buckets = OrderedDict()
    if bucket_kind == "day":
        for i in range(days):
            d = start_date + timedelta(days=i)
            buckets[d.isoformat()] = {
                "date": d.isoformat(),
                "weekday": _WEEKDAY_FROM_SAT.get(d.weekday(), ""),
                "deposit": 0.0,
                "withdraw": 0.0,
            }
    else:
        for w in range(13):
            d = start_date + timedelta(days=7 * w)
            buckets[d.isoformat()] = {
                "date": d.isoformat(),
                "weekday": f"هفته {w + 1}",
                "deposit": 0.0,
                "withdraw": 0.0,
            }

    def bucket_key(d_iso: str):
        if bucket_kind == "day":
            return d_iso if d_iso in buckets else None
        try:
            dt = datetime.strptime(d_iso, "%Y-%m-%d").date()
        except Exception:
            return None
        delta = (dt - start_date).days
        if delta < 0 or delta >= 91:
            return None
        return (start_date + timedelta(days=(delta // 7) * 7)).isoformat()

    deposit_total = 0.0
    withdraw_total = 0.0
    cat_buckets = {}  # فقط برداشت برای donut
    acc_buckets = {}
    tx_count = 0
    for t in all_tx:
        if t.account_id not in scope_ids:
            continue
        dt = _parse_transaction_date(getattr(t, "transaction_date", None))
        if not dt:
            continue
        key = bucket_key(dt.date().isoformat())
        if not key:
            continue
        tx_count += 1
        amount = float(t.amount or 0)
        ttype = t.transaction_type
        entry = acc_buckets.setdefault(t.account_id, {"account_id": t.account_id, "deposit": 0.0, "withdraw": 0.0, "count": 0})
        entry["count"] += 1
        if ttype == "deposit":
            buckets[key]["deposit"] += amount
            deposit_total += amount
            entry["deposit"] += amount
        elif ttype == "withdrawal":
            buckets[key]["withdraw"] += amount
            withdraw_total += amount
            entry["withdraw"] += amount
            cat = (t.category or "other_out")
            cat_buckets[cat] = cat_buckets.get(cat, 0.0) + amount

    balance_net = deposit_total - withdraw_total

    # پرهزینه‌ترین دسته
    top_category = None
    if cat_buckets:
        top_cat_id = max(cat_buckets, key=cat_buckets.get)
        top_category = {"id": top_cat_id, "amount": cat_buckets[top_cat_id]}

    # breakdown با درصد
    category_breakdown = []
    for cat_id, amt in sorted(cat_buckets.items(), key=lambda x: -x[1]):
        pct = (amt / withdraw_total * 100) if withdraw_total > 0 else 0.0
        category_breakdown.append({
            "id": cat_id,
            "amount": amt,
            "percent": round(pct, 1),
        })

    account_breakdown = sorted(acc_buckets.values(), key=lambda e: -(e["deposit"] + e["withdraw"]))

    return {
        "days": days,
        "bucket": bucket_kind,
        "range_start": start_date.isoformat(),
        "range_end": today.isoformat(),
        "scope_account_ids": sorted(scope_ids),
        "summary": {
            "deposit_total": deposit_total,
            "withdraw_total": withdraw_total,
            "balance_net": balance_net,
            "top_category": top_category,
            "transaction_count": tx_count,
        },
        "daily_buckets": list(buckets.values()),
        "category_breakdown": category_breakdown,
        "account_breakdown": account_breakdown,
    }