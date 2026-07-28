from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, Float
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

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
    sub_goal = relationship("SubGoal", backref="linked_tasks")
    goal = relationship("Goal", backref="linked_tasks")

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
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    status = Column(String, default="not_started")
    progress_percent = Column(Integer, default=0)
    order_index = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = relationship("Goal", backref="sub_goals")

class SubGoalTask(Base, TimestampMixin):
    __tablename__ = "sub_goal_tasks"
    id = Column(Integer, primary_key=True, index=True)
    sub_goal_id = Column(Integer, ForeignKey("sub_goals.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    due_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sub_goal = relationship("SubGoal", backref="tasks")

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
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan", order_by="Transaction.transaction_date.desc()")

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(Date, nullable=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, default=0)
    description = Column(Text, nullable=True)
    balance_after = Column(Float, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account = relationship("Account", back_populates="transactions")
    owner = relationship("User")

class Movie(Base, TimestampMixin):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=True)  # action, comedy, drama, horror, sci-fi, animation, documentary, other
    register_date = Column(Date, nullable=True)
    watch_date = Column(Date, nullable=True)
    rating = Column(Integer, default=0)  # 1 to 10
    notes = Column(Text, nullable=True)
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
    rating = Column(Integer, default=0)  # 1 to 5
    notes = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_favorite = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")