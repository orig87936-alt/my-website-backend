"""
Test script to debug article creation issue
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.schemas.article import ArticleCreate, ContentBlock
from app.services.article import article_service
from app.models.base import Base

# Database URL - use the same as in .env
from app.config import get_settings
settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

async def test_create_article():
    # Create async engine
    print(f"Using database: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Don't create tables - they should already exist
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Load test data
    with open('../test-manus-full.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Test data loaded")
    print(f"Title (ZH): {data.get('title_zh', 'N/A')}")
    print(f"Category: {data.get('category', 'N/A')}")
    
    # Create article
    async with async_session() as session:
        try:
            print("\nCreating article...")
            article_data = ArticleCreate(**data)
            print("ArticleCreate schema validated successfully")

            article = await article_service.create_article(session, article_data)
            print(f"Article created successfully: {article.id}")
            print(f"Title: {article.title_zh}")
            print(f"Category: {article.category}")
            print(f"Content blocks (ZH): {len(article.content_zh)}")
            print(f"Content blocks (EN): {len(article.content_en)}")

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_create_article())

