"""List all articles in the database"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.article import Article
from sqlalchemy import select

async def list_articles():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Article.id, Article.title_en, Article.category)
            .order_by(Article.published_at.desc())
        )
        articles = result.all()
        
        print(f"\n📚 Found {len(articles)} articles in database:\n")
        for id, title, category in articles:
            print(f"  [{category}] {id}")
            print(f"    Title: {title}\n")

if __name__ == "__main__":
    asyncio.run(list_articles())

