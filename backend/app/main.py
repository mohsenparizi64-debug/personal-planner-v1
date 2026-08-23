from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.models.all_models import *  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # ۱. ساخت تمامی جدول‌های جدید در دیتابیس
        await conn.run_sync(Base.metadata.create_all)

        # ۲. مایگریشن اتوماتیک ستون‌های جدید بیومتریک به جدول users
        try:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            new_user_columns = [
                ("birth_date", "DATE"),
                ("gender", "VARCHAR"),
                ("height", "FLOAT"),
                ("weight", "FLOAT"),
                ("target_weight", "FLOAT"),
                ("activity_level", "VARCHAR"),
                ("health_notes", "TEXT"),
                ("ai_persona_tone", "VARCHAR DEFAULT 'friendly_expert'"),
            ]

            for col_name, col_type in new_user_columns:
                if col_name not in columns:
                    await conn.execute(
                        text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    )
                    print(
                        f"✅ Auto-migrated column '{col_name}' added to 'users' table."
                    )
        except Exception as e:
            print(f"User migration note: {e}")

        # ۳. مایگریشن اتوماتیک ستون‌های جدید تسک‌ها
        try:
            result_t = await conn.execute(text("PRAGMA table_info(tasks)"))
            t_columns = [row[1] for row in result_t.fetchall()]

            if "is_infinite_recurrence" not in t_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE tasks ADD COLUMN is_infinite_recurrence BOOLEAN DEFAULT 1"
                    )
                )
                print(
                    "✅ Auto-migrated 'is_infinite_recurrence' added to 'tasks'."
                )

            if "auto_reschedule" not in t_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE tasks ADD COLUMN auto_reschedule BOOLEAN DEFAULT 1"
                    )
                )
                print("✅ Auto-migrated 'auto_reschedule' added to 'tasks'.")
        except Exception as e:
            print(f"Tasks migration note: {e}")

        # ۴. مایگریشن اتوماتیک ستون‌های تاریخ اهداف معنوی
        try:
            result_sp = await conn.execute(
                text("PRAGMA table_info(spiritual_trackers)")
            )
            sp_columns = [row[1] for row in result_sp.fetchall()]

            if "register_date" not in sp_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE spiritual_trackers ADD COLUMN register_date DATE"
                    )
                )
            if "last_action_date" not in sp_columns:
                await conn.execute(
                    text(
                        "ALTER TABLE spiritual_trackers ADD COLUMN last_action_date DATE"
                    )
                )
        except Exception as e:
            print(f"Spiritual migration note: {e}")

        # ۵. مایگریشن اتوماتیک ستون‌های ایده‌ها
        try:
            result_ideas = await conn.execute(
                text("PRAGMA table_info(ideas)")
            )
            idea_columns = [row[1] for row in result_ideas.fetchall()]

            if "sub_goal_id" not in idea_columns:
                await conn.execute(
                    text("ALTER TABLE ideas ADD COLUMN sub_goal_id INTEGER")
                )
            if "conversion_date" not in idea_columns:
                await conn.execute(
                    text("ALTER TABLE ideas ADD COLUMN conversion_date DATE")
                )
        except Exception as e:
            print(f"Ideas migration note: {e}")

    yield


app = FastAPI(title="Personal Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # برای اجازه دسترسی تمام پورت‌ها و IPهای فرانت‌اند
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.goals import router as goals_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.finance import router as finance_router
from app.api.v1.movies import router as movies_router
from app.api.v1.books import router as books_router
from app.api.v1.places import router as places_router
from app.api.v1.backup import router as backup_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.ideas import router as ideas_router
from app.api.v1.mentor import router as mentor_router
from app.api.v1.bio_tracker import router as bio_router
from app.api.v1.skills import router as skills_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(goals_router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(roadmap_router, prefix="/api/v1/roadmap", tags=["roadmap"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(movies_router, prefix="/api/v1/movies", tags=["movies"])
app.include_router(books_router, prefix="/api/v1/books", tags=["books"])
app.include_router(places_router, prefix="/api/v1/places", tags=["places"])
app.include_router(backup_router, prefix="/api/v1/backup", tags=["backup"])
app.include_router(
    dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"]
)
app.include_router(ideas_router, prefix="/api/v1/ideas", tags=["ideas"])
app.include_router(mentor_router, prefix="/api/v1/mentor", tags=["mentor"])
app.include_router(bio_router, prefix="/api/v1/bio", tags=["bio"])
app.include_router(skills_router, prefix="/api/v1/skills", tags=["skills"])


@app.get("/")
async def root():
    return {"message": "Personal Planner API is running"}