from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.base import Base
from app.db.session import engine
from app.models.all_models import *  # noqa

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Personal Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(goals_router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(roadmap_router, prefix="/api/v1/roadmap", tags=["roadmap"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(movies_router, prefix="/api/v1/movies", tags=["movies"])
app.include_router(books_router, prefix="/api/v1/books", tags=["books"])
app.include_router(places_router, prefix="/api/v1/places", tags=["places"])
app.include_router(backup_router, prefix="/api/v1/backup", tags=["backup"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(ideas_router, prefix="/api/v1/ideas", tags=["ideas"])
app.include_router(mentor_router, prefix="/api/v1/mentor", tags=["mentor"])


@app.get("/")
async def root():
    return {"message": "Personal Planner API is running"}