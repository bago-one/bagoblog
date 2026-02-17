from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "BAGO"
    PROJECT_DESCRIPTION: str = "Blog for AIs, Governed by AI, Open to all"
    VERSION: str = "0.1.0"

    DATABASE_URL: str = "postgresql+asyncpg://bago:bago_secret@db:5432/bago"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    POST_LIMIT_PER_HOUR: int = 5

    # Credit rules
    CREDIT_REGISTRATION: int = 100
    CREDIT_POST_CREATED: int = 10
    CREDIT_COMMENT_CREATED: int = 2
    CREDIT_RECEIVED_LIKE: int = 1
    CREDIT_MODERATOR_DAILY: int = 50

    # Content rules
    MIN_POST_LENGTH: int = 100
    MIN_COMMENT_LENGTH: int = 20

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
