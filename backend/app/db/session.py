from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from app.core.config import settings

# موتور دیتابیس بدون لاگ‌های سنگین ترمینال برای سرعت حداکثری
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,  # غیرفعال‌سازی لاگ ترمینال برای افزایش سرعت
    connect_args={"timeout": 30}
)

# فعال‌سازی تنظیمات پرسرعت دیتابیس SQLite (WAL Mode + Memory Cache)
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA cache_size=10000;")
    cursor.execute("PRAGMA temp_store=MEMORY;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.close()

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session