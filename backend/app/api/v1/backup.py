from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import io
from datetime import datetime, date
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.all_models import User, Task, Goal, GoalLog, SubGoal, SubGoalTask, KPI, Account, Transaction, Movie, Book, Place

router = APIRouter()

def serialize_date(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def parse_date(val):
    """تبدیل رشته تاریخ به date یا datetime"""
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val
    try:
        s = str(val)[:19]  # 2024-01-01T12:00:00
        if 'T' in s:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except:
        return None

def safe_set_attrs(obj, data, exclude_keys, date_keys):
    """تنظیم امن فیلدها با تبدیل تاریخ"""
    for k, v in data.items():
        if k in exclude_keys:
            continue
        if k in date_keys:
            v = parse_date(v)
        try:
            setattr(obj, k, v)
        except:
            pass  # فیلدهایی که وجود ندارن رو ignore کن

DATE_KEYS_COMMON = ['created_at', 'updated_at']
DATE_KEYS_GOAL = ['start_date', 'target_date'] + DATE_KEYS_COMMON
DATE_KEYS_TASK = ['register_date', 'due_date', 'last_action_date', 'recurrence_end_date'] + DATE_KEYS_COMMON
DATE_KEYS_SG = ['start_date', 'target_date'] + DATE_KEYS_COMMON
DATE_KEYS_ACCOUNT = ['register_date'] + DATE_KEYS_COMMON
DATE_KEYS_TRANS = ['transaction_date'] + DATE_KEYS_COMMON
DATE_KEYS_MOVIE = ['register_date', 'watch_date'] + DATE_KEYS_COMMON
DATE_KEYS_BOOK = ['register_date', 'read_date'] + DATE_KEYS_COMMON
DATE_KEYS_PLACE = ['register_date', 'visit_date'] + DATE_KEYS_COMMON
DATE_KEYS_KPI = ['last_updated'] + DATE_KEYS_COMMON

async def get_all_user_data(db: AsyncSession, user_id: int):
    tasks_result = await db.execute(select(Task).where(Task.owner_id == user_id))
    tasks = []
    for t in tasks_result.scalars().all():
        tasks.append({"title": t.title, "description": t.description, "register_date": t.register_date,
            "due_date": t.due_date, "category": t.category, "sub_goal_id": t.sub_goal_id, "goal_id": t.goal_id,
            "last_action_date": t.last_action_date, "status": t.status, "recurrence_type": t.recurrence_type,
            "recurrence_interval": t.recurrence_interval, "recurrence_end_date": t.recurrence_end_date,
            "priority": t.priority, "is_completed": t.is_completed, "created_at": t.created_at, "updated_at": t.updated_at})
    
    goals_result = await db.execute(select(Goal).where(Goal.owner_id == user_id))
    goals = []
    for g in goals_result.scalars().all():
        goals.append({"title": g.title, "description": g.description, "start_date": g.start_date,
            "target_date": g.target_date, "current_status": g.current_status, "current_obstacle": g.current_obstacle,
            "next_step": g.next_step, "priority": g.priority, "success_criteria": g.success_criteria,
            "is_completed": g.is_completed, "progress_percent": g.progress_percent,
            "created_at": g.created_at, "updated_at": g.updated_at})
    
    logs_result = await db.execute(select(GoalLog).where(GoalLog.owner_id == user_id))
    logs = [{"goal_id": l.goal_id, "action": l.action, "field_name": l.field_name, "old_value": l.old_value,
             "new_value": l.new_value, "description": l.description, "created_at": l.created_at} for l in logs_result.scalars().all()]
    
    sg_result = await db.execute(select(SubGoal).where(SubGoal.owner_id == user_id))
    sub_goals = [{"goal_id": sg.goal_id, "title": sg.title, "description": sg.description, "start_date": sg.start_date,
                  "target_date": sg.target_date, "status": sg.status, "progress_percent": sg.progress_percent,
                  "order_index": sg.order_index, "created_at": sg.created_at, "updated_at": sg.updated_at} for sg in sg_result.scalars().all()]
    
    sgt_result = await db.execute(select(SubGoalTask).where(SubGoalTask.owner_id == user_id))
    sub_tasks = [{"sub_goal_id": st.sub_goal_id, "title": st.title, "is_completed": st.is_completed,
                  "priority": st.priority, "due_date": st.due_date, "created_at": st.created_at, "updated_at": st.updated_at} for st in sgt_result.scalars().all()]
    
    kpi_result = await db.execute(select(KPI).where(KPI.owner_id == user_id))
    kpis = [{"goal_id": k.goal_id, "title": k.title, "unit": k.unit, "target_value": k.target_value,
             "current_value": k.current_value, "frequency": k.frequency, "last_updated": k.last_updated,
             "created_at": k.created_at, "updated_at": k.updated_at} for k in kpi_result.scalars().all()]
    
    acc_result = await db.execute(select(Account).where(Account.owner_id == user_id))
    accounts = [{"name": a.name, "bank_name": a.bank_name, "sheba_number": a.sheba_number,
                 "current_balance": a.current_balance, "register_date": a.register_date,
                 "created_at": a.created_at, "updated_at": a.updated_at} for a in acc_result.scalars().all()]
    
    trans_result = await db.execute(select(Transaction).where(Transaction.owner_id == user_id))
    transactions = [{"account_id": t.account_id, "transaction_date": t.transaction_date, "transaction_type": t.transaction_type,
                     "amount": t.amount, "description": t.description, "balance_after": t.balance_after,
                     "created_at": t.created_at, "updated_at": t.updated_at} for t in trans_result.scalars().all()]
    
    movie_result = await db.execute(select(Movie).where(Movie.owner_id == user_id))
    movies = [{"title": m.title, "category": m.category, "register_date": m.register_date, "watch_date": m.watch_date,
               "rating": m.rating, "notes": m.notes, "is_watched": m.is_watched,
               "created_at": m.created_at, "updated_at": m.updated_at} for m in movie_result.scalars().all()]
    
    book_result = await db.execute(select(Book).where(Book.owner_id == user_id))
    books = [{"title": b.title, "author": b.author, "category": b.category, "register_date": b.register_date,
              "read_date": b.read_date, "rating": b.rating, "notes": b.notes, "is_read": b.is_read,
              "created_at": b.created_at, "updated_at": b.updated_at} for b in book_result.scalars().all()]
    
    place_result = await db.execute(select(Place).where(Place.owner_id == user_id))
    places = [{"name": p.name, "category": p.category, "address": p.address, "description": p.description,
               "register_date": p.register_date, "is_visited": p.is_visited, "visit_date": p.visit_date,
               "rating": p.rating, "notes": p.notes, "latitude": p.latitude, "longitude": p.longitude,
               "is_favorite": p.is_favorite, "created_at": p.created_at, "updated_at": p.updated_at} for p in place_result.scalars().all()]
    
    return {"version": "1.0", "exported_at": datetime.utcnow().isoformat(),
        "tasks": tasks, "goals": goals, "goal_logs": logs, "sub_goals": sub_goals, "sub_goal_tasks": sub_tasks,
        "kpis": kpis, "accounts": accounts, "transactions": transactions,
        "movies": movies, "books": books, "places": places}

@router.get("/export")
async def export_backup(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = await get_all_user_data(db, current_user.id)
    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=serialize_date)
    return StreamingResponse(io.BytesIO(json_str.encode('utf-8')), media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=backup_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"})

@router.post("/import")
async def import_backup(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
    except:
        raise HTTPException(400, "Invalid JSON file")
    
    # حذف دیتای قبلی
    for model in [Task, SubGoalTask, KPI, Transaction, GoalLog, SubGoal, Account, Movie, Book, Place, Goal]:
        result = await db.execute(select(model).where(model.owner_id == current_user.id))
        for obj in result.scalars().all():
            await db.delete(obj)
    await db.commit()
    
    # Goals
    goal_id_map = {}
    for g in data.get("goals", []):
        ng = Goal(owner_id=current_user.id)
        safe_set_attrs(ng, g, ['id'], DATE_KEYS_GOAL)
        db.add(ng); await db.flush()
        goal_id_map[g.get("id")] = ng.id
    
    # SubGoals
    sg_id_map = {}
    for sg in data.get("sub_goals", []):
        nsg = SubGoal(owner_id=current_user.id, goal_id=goal_id_map.get(sg.get("goal_id"), sg.get("goal_id")))
        safe_set_attrs(nsg, sg, ['id', 'goal_id'], DATE_KEYS_SG)
        db.add(nsg); await db.flush()
        sg_id_map[sg.get("id")] = nsg.id
    
    # Tasks
    for t in data.get("tasks", []):
        nt = Task(owner_id=current_user.id, goal_id=goal_id_map.get(t.get("goal_id")), sub_goal_id=sg_id_map.get(t.get("sub_goal_id")))
        safe_set_attrs(nt, t, ['id', 'goal_id', 'sub_goal_id', 'owner_id'], DATE_KEYS_TASK)
        db.add(nt)
    
    # SubGoalTasks
    for st in data.get("sub_goal_tasks", []):
        nst = SubGoalTask(owner_id=current_user.id, sub_goal_id=sg_id_map.get(st.get("sub_goal_id")))
        safe_set_attrs(nst, st, ['id', 'sub_goal_id', 'owner_id'], ['due_date'] + DATE_KEYS_COMMON)
        db.add(nst)
    
    # KPIs
    for k in data.get("kpis", []):
        nk = KPI(owner_id=current_user.id, goal_id=goal_id_map.get(k.get("goal_id")))
        safe_set_attrs(nk, k, ['id', 'goal_id', 'owner_id'], DATE_KEYS_KPI)
        db.add(nk)
    
    # Accounts
    acc_id_map = {}
    for a in data.get("accounts", []):
        na = Account(owner_id=current_user.id)
        safe_set_attrs(na, a, ['id'], DATE_KEYS_ACCOUNT)
        db.add(na); await db.flush()
        acc_id_map[a.get("id")] = na.id
    
    # Transactions
    for t in data.get("transactions", []):
        nt = Transaction(owner_id=current_user.id, account_id=acc_id_map.get(t.get("account_id")))
        safe_set_attrs(nt, t, ['id', 'account_id', 'owner_id'], DATE_KEYS_TRANS)
        db.add(nt)
    
    # Movies
    for m in data.get("movies", []):
        nm = Movie(owner_id=current_user.id)
        safe_set_attrs(nm, m, ['id'], DATE_KEYS_MOVIE)
        db.add(nm)
    
    # Books
    for b in data.get("books", []):
        nb = Book(owner_id=current_user.id)
        safe_set_attrs(nb, b, ['id'], DATE_KEYS_BOOK)
        db.add(nb)
    
    # Places
    for p in data.get("places", []):
        np = Place(owner_id=current_user.id)
        safe_set_attrs(np, p, ['id'], DATE_KEYS_PLACE)
        db.add(np)
    
    # GoalLogs - فقط با goal_id معتبر
    for l in data.get("goal_logs", []):
        mapped_goal_id = goal_id_map.get(l.get("goal_id"))
        if mapped_goal_id:
            nl = GoalLog(owner_id=current_user.id, goal_id=mapped_goal_id)
            safe_set_attrs(nl, l, ['id', 'goal_id', 'owner_id'], DATE_KEYS_COMMON)
            db.add(nl)
    
    await db.commit()
    return {"message": "Backup restored successfully", "counts": {
        "tasks": len(data.get("tasks", [])), "goals": len(data.get("goals", [])),
        "movies": len(data.get("movies", [])), "books": len(data.get("books", [])),
        "places": len(data.get("places", [])), "accounts": len(data.get("accounts", []))}}