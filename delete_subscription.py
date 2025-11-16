"""
Temporary script to delete a subscription by email
"""
import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.models.subscription import Subscription


async def delete_subscription_by_email(email: str):
    """Delete a subscription by email"""
    # Database URL
    database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/newsdb"

    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=True,
    )
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Delete subscription
        result = await session.execute(
            delete(Subscription).where(Subscription.email == email)
        )
        await session.commit()
        
        print(f"Deleted {result.rowcount} subscription(s) for email: {email}")
    
    await engine.dispose()


if __name__ == "__main__":
    email_to_delete = "test@example.com"
    asyncio.run(delete_subscription_by_email(email_to_delete))

