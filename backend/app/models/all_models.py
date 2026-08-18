from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from datetime import datetime

# ==========================================
# ۱. جدول کاربران (User)
# ==========================================
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
    
    # فیلدهای بیومتریک، وزن هدف و پرسونای AI
    birth_date = Column(Date, nullable=True)               # تاریخ تولد
    gender = Column(String, nullable=True)                  # جنسیت (مرد / زن)
    height = Column(Float, nullable=True)                   # قد (سانتی‌متر)
    weight = Column(Float, nullable=True)                   # وزن اولیه / کنونی (کیلوگرم)
    target_weight = Column(Float, nullable=True)            # وزن هدف (کیلوگرم)
    activity_level = Column(String, nullable=True)          # سطح فعالیت
    health_notes = Column(Text, nullable=True)              # ملاحظات پزشکی یا رژیمی
    ai_persona_tone = Column(String, default="friendly_expert") # لحن منتور

# ==========================================
# ۲. جدول تسک‌های اجرایی (Task)
# ==========================================
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
    is_infinite_recurrence = Column(Boolean, default=True)  # مداومت دوره تکرار
    priority = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    auto_reschedule = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    sub_goal = relationship("SubGoal", back_populates="main_tasks")
    goal = relationship("Goal", back_populates="main_tasks")

# ==========================================
# ۳. جدول اهداف کلان (Goal)
# ==========================================
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

# ==========================================
# ۴. جدول لاگ اهداف (GoalLog)
# ==========================================
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

# ==========================================
# ۵. جدول گام‌های عملیاتی نقشه راه (SubGoal)
# ==========================================
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

# ==========================================
# ۶. جدول تسک‌های اختصاصی گام عملیاتی (SubGoalTask)
# ==========================================
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

# ==========================================
# ۷. جدول شاخص‌های کلیدی عملکرد (KPI)
# ==========================================
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

# ==========================================
# ۸. جدول حساب‌های مالی (Account)
# ==========================================
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

# ==========================================
# ۹. جدول تراکنش‌های مالی (Transaction)
# ==========================================
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

# ==========================================
# ۱۰. جدول آرشیو فیلم‌ها (Movie)
# ==========================================
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

# ==========================================
# ۱۱. جدول آرشیو کتاب‌ها (Book)
# ==========================================
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

# ==========================================
# ۱۲. جدول آرشیو مکان‌ها (Place)
# ==========================================
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
# ۱۳. جدول بانک ایده‌ها (Idea)
# ==========================================
class Idea(Base, TimestampMixin):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="عمومی")
    status = Column(String, default="raw")
    excitement_rating = Column(Integer, default=3)
    reference_links = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)
    
    # اتصالات استراتژیک ۳ لایه‌ای
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    sub_goal_id = Column(Integer, ForeignKey("sub_goals.id", ondelete="SET NULL"), nullable=True)
    
    # اتصالات تبدیل و تاریخ
    converted_to_goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    converted_to_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    conversion_date = Column(Date, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    goal = relationship("Goal", foreign_keys=[goal_id])
    sub_goal = relationship("SubGoal", foreign_keys=[sub_goal_id])

# ==========================================
# ۱۴. جدول اهداف معنوی (SpiritualTracker)
# ==========================================
class SpiritualTracker(Base, TimestampMixin):
    __tablename__ = "spiritual_trackers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    tracker_type = Column(String, default="prayer_qada")
    total_needed = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    unit = Column(String, default="روز")
    register_date = Column(Date, nullable=True)
    last_action_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    logs = relationship("SpiritualLog", back_populates="tracker", cascade="all, delete-orphan")

# ==========================================
# ۱۵. جدول لاگ‌های معنوی (SpiritualLog)
# ==========================================
class SpiritualLog(Base, TimestampMixin):
    __tablename__ = "spiritual_logs"
    id = Column(Integer, primary_key=True, index=True)
    tracker_id = Column(Integer, ForeignKey("spiritual_trackers.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)
    log_time = Column(String, nullable=True)
    count_change = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    tracker = relationship("SpiritualTracker", back_populates="logs")
    owner = relationship("User")

# ==========================================
# ۱۶. جدول لاگ‌های سلامت و وزن (HealthLog)
# ==========================================
class HealthLog(Base, TimestampMixin):
    __tablename__ = "health_logs"
    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")

# ==========================================
# ۱۷. جدول فعالیت‌های ورزشی (WorkoutLog)
# ==========================================
class WorkoutLog(Base, TimestampMixin):
    __tablename__ = "workout_logs"
    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False)
    log_time = Column(String, nullable=True)
    workout_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")

# ==========================================
# ۱۸. جدول وعده‌های غذایی (MealLog)
# ==========================================
class MealLog(Base, TimestampMixin):
    __tablename__ = "meal_logs"
    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False)
    log_time = Column(String, nullable=True)
    meal_type = Column(String, nullable=False)
    food_name = Column(String, nullable=False)
    portion_unit = Column(String, nullable=False)
    calories = Column(Integer, default=0)
    temperament = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")

# ==========================================
# ۱۹. جدول عادات (Habit)
# ==========================================
class Habit(Base, TimestampMixin):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, default="سلامتی")
    frequency = Column(String, default="daily")
    target_days_per_week = Column(Integer, default=7)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

# ==========================================
# ۲۰. جدول لاگ عادات (HabitLog)
# ==========================================
class HabitLog(Base, TimestampMixin):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)
    is_completed = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    habit = relationship("Habit", back_populates="logs")
    owner = relationship("User")

# ==========================================
# ۲۱. جدول بانک مهارت‌ها (Skill)
# ==========================================
class Skill(Base, TimestampMixin):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)
    status = Column(String, default="in_progress")
    progress_percent = Column(Integer, default=0)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    goal = relationship("Goal", foreign_keys=[goal_id])
    learning_logs = relationship("LearningLog", back_populates="skill", cascade="all, delete-orphan")

# ==========================================
# ۲۲. جدول لاگ‌های آموزه و یادگیری (LearningLog)
# ==========================================
class LearningLog(Base, TimestampMixin):
    __tablename__ = "learning_logs"
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    log_date = Column(Date, nullable=False)
    resource_url = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User")
    skill = relationship("Skill", back_populates="learning_logs")