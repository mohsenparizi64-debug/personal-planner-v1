from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./planner.db"
    SECRET_KEY: str = "my-secret-key-change-this-123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 🔑 کلید هوش مصنوعی AvalAI (بدون تحریم و بدون نیاز به قندشکن)
    AVALAI_API_KEY: str = "aa-W7dj6J4hjbDQALyrA1ozndnWvWyA45Div8YCTqau3GgnIoVv"

    class Config:
        env_file = ".env"

settings = Settings()