import asyncio
from app.database import get_db
from app.models.article import Article
from sqlalchemy import select

async def list_articles():
    async for db in get_db():
        result = await db.execute(select(Article).order_by(Article.created_at.desc()))
        articles = result.scalars().all()
        
        print(f"\n{'='*80}")
        print(f"Total articles: {len(articles)}")
        print(f"{'='*80}\n")
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. ID: {article.id}")
            print(f"   Title ZH: {article.title_zh}")
            print(f"   Title EN: {article.title_en}")
            print(f"   Summary ZH length: {len(article.summary_zh) if article.summary_zh else 0}")
            print(f"   Summary EN length: {len(article.summary_en) if article.summary_en else 0}")
            print(f"   Created: {article.created_at}")
            print()
        break

asyncio.run(list_articles())

