from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from datetime import datetime

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    register_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    duration_days = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    sub_goal_id = Column(Integer, ForeignKey("sub_goals.id", ondelete="SET NULL"), nullable=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    last_action_date = Column(Date, nullable=True)
    status = Column(String, default="not_started")
    recurrence_type = Column(String, nullable=True)
    recurrence_interval = Column(Integer, default=1)
    recurrence_end_date = Column(Date, nullable=True)
    priority = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    sub_goal = relationship("SubGoal", back_populates="main_tasks")
    goal = relationship("Goal", back_populates="main_tasks")

class Goal(Base, TimestampMixin):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    current_status = Column(Text, nullable=True)
    current_obstacle = Column(Text, nullable=True)
    next_step = Column(Text, nullable=True)
    priority = Column(Integer, default=0)
    success_criteria = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    progress_percent = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    sub_goals = relationship("SubGoal", back_populates="goal", cascade="all, delete-orphan")
    main_tasks = relationship("Task", back_populates="goal")

class GoalLog(Base, TimestampMixin):
    __tablename__ = "goal_logs"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    field_name = Column(String, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = relationship("Goal", backref="logs")

class SubGoal(Base, TimestampMixin):
    __tablename__ = "sub_goals"
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    target_date = Column(String, nullable=True)
    status = Column(String, default="not_started")
    progress_percent = Column(Integer, default=0)
    order_index = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    goal = relationship("Goal", back_populates="sub_goals")
    dedicated_tasks = relationship("SubGoalTask", back_populates="sub_goal", cascade="all, delete-orphan")
    main_tasks = relationship("Task", back_populates="sub_goal")

class SubGoalTask(Base, TimestampMixin):
    __tablename__ = "sub_goal_tasks"
    id = Column(Integer, primary_key=True)
    sub_goal_id = Column(Integer, ForeignKey("sub_goals.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    due_date = Column(String, nullable=True)
    description = Column(String, nullable=True)
    last_action_date = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    sub_goal = relationship("SubGoal", back_populates="dedicated_tasks")

class KPI(Base, TimestampMixin):
    __tablename__ = "kpis"
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    target_value = Column(Float, default=0)
    current_value = Column(Float, default=0)
    frequency = Column(String, default="monthly")
    last_updated = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = relationship("Goal", backref="kpis")

class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bank_name = Column(String, nullable=True)
    sheba_number = Column(String, nullable=True)
    current_balance = Column(Float, default=0)
    register_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    transaction_date = Column(String)
    transaction_type = Column(String)
    amount = Column(Float)
    category = Column(String, nullable=False)
    items = Column(String, nullable=True)
    description = Column(String, nullable=True)
    balance_after = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    account = relationship("Account", back_populates="transactions")

class Movie(Base, TimestampMixin):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    movie_type = Column(String, default="movie")
    category = Column(String, nullable=True)
    origin = Column(String, default="foreign")
    register_date = Column(Date, nullable=True)
    watch_date = Column(Date, nullable=True)
    rating = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    poster_url = Column(Text, nullable=True)
    imdb_url = Column(Text, nullable=True)
    is_watched = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")

class Book(Base, TimestampMixin):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    category = Column(String, nullable=True)
    register_date = Column(Date, nullable=True)
    read_date = Column(Date, nullable=True)
    rating = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")

class Place(Base, TimestampMixin):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    address = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    register_date = Column(Date, nullable=True)
    is_visited = Column(Boolean, default=False)
    visit_date = Column(Date, nullable=True)
    rating = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_favorite = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")

# ==========================================
# کلاس جدید: بانک ایده‌ها (Idea)
# ==========================================
class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="عمومی")
    status = Column(String, default="raw")             # raw (خام), in_review (در حال بررسی), ready (جاه‌طلبانه/آماده اجرا), archived (بایگانی)
    excitement_rating = Column(Integer, default=3)      # درجه هیجان (۱ تا ۵ ستاره)
    reference_links = Column(Text, nullable=True)      # لینک‌ها و منابع الگوبرداری
    tags = Column(String, nullable=True)               # هشتگ‌ها/برچسب‌ها (با کاما جدا شده)
    is_archived = Column(Boolean, default=False)
    
    # لینک اختیاری به هدف و اتصال‌های تبدیل هوشمند
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    converted_to_goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    converted_to_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    goal = relationship("Goal", foreign_keys=[goal_id])