import asyncio
from app.database import get_db
from app.models.article import Article
from sqlalchemy import select

async def check():
    async for db in get_db():
        result = await db.execute(select(Article).limit(3))
        articles = result.scalars().all()
        
        for i, article in enumerate(articles, 1):
            print(f"\n{'='*60}")
            print(f"Article {i}: {article.title_zh[:50]}")
            print(f"{'='*60}")
            print(f"Summary ZH length: {len(article.summary_zh) if article.summary_zh else 0}")
            print(f"Summary EN length: {len(article.summary_en) if article.summary_en else 0}")
            print(f"Lead ZH length: {len(article.lead_zh) if article.lead_zh else 0}")
            print(f"Lead EN length: {len(article.lead_en) if article.lead_en else 0}")
            print(f"\nSummary ZH: {article.summary_zh[:100] if article.summary_zh else 'None'}...")
            print(f"Lead ZH: {article.lead_zh[:100] if article.lead_zh else 'None'}...")
        break

asyncio.run(check())

