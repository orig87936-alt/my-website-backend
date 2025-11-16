from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "S&L News API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # DeepSeek API
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 1000
    DEEPSEEK_TEMPERATURE: float = 0.7

    # OpenAI (for embeddings)
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days (7 * 24 * 60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7  # Legacy, for backward compatibility

    # CORS (comma-separated string)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Email
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "News Platform"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FRONTEND_URL: str = "http://localhost:3000"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Appointments
    APPOINTMENT_TIME_SLOTS: str = "09:00,09:30,10:00,10:30,11:00,11:30,13:00,13:30,14:00,14:30,15:00,15:30,16:00,16:30,17:00,17:30"
    EMAIL_RETRY_MAX_ATTEMPTS: int = 3
    EMAIL_RETRY_DELAYS: str = "60,300,1800"

    # Chat
    CHAT_RESPONSE_TIMEOUT: int = 3
    VECTOR_SEARCH_LIMIT: int = 5

    # Translation Service
    TRANSLATION_PROVIDER: str = "deepseek"
    DEEPL_API_KEY: str = "your-deepl-api-key-here"
    TRANSLATION_CACHE_DAYS: int = 30

    # Document Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_FILE_TYPES: str = ".md,.docx"
    TEMP_UPLOAD_DIR: str = "./temp_uploads"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

@lru_cache()
def get_settings():
    return Settings()

