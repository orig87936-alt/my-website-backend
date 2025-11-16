"""
数据库类型适配器
根据数据库类型自动选择合适的列类型
"""
from sqlalchemy import String, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from app.config import get_settings

# 检测数据库类型
settings = get_settings()
is_sqlite = 'sqlite' in settings.DATABASE_URL.lower()

# UUID 类型
# SQLite 使用 String(36)，PostgreSQL 使用 UUID
if is_sqlite:
    UUID = String(36)
else:
    UUID = PG_UUID(as_uuid=True)

# JSON 类型
# SQLite 使用 JSON，PostgreSQL 使用 JSONB
if is_sqlite:
    JSONB = JSON
else:
    JSONB = PG_JSONB

