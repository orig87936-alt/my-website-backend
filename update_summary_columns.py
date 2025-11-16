"""
Script to update article summary column lengths in the database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def update_columns():
    """Update summary column lengths"""
    # Get DATABASE_URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://newsuser:newspass123@localhost:5432/newsdb')
    # Convert asyncpg URL to connection parameters
    # Format: postgresql+asyncpg://user:pass@host:port/dbname
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"Connecting to database...")
    conn = await asyncpg.connect(db_url)
    
    try:
        print("Updating summary_zh column to VARCHAR(150)...")
        await conn.execute("""
            ALTER TABLE articles 
            ALTER COLUMN summary_zh TYPE VARCHAR(150);
        """)
        print("✅ summary_zh updated successfully")
        
        print("Updating summary_en column to VARCHAR(300)...")
        await conn.execute("""
            ALTER TABLE articles 
            ALTER COLUMN summary_en TYPE VARCHAR(300);
        """)
        print("✅ summary_en updated successfully")
        
        print("\n🎉 All columns updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(update_columns())

