"""
Update enum values in database from lowercase to uppercase
"""
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal


async def update_enum_values():
    """Update enum values to uppercase"""
    async with AsyncSessionLocal() as db:
        try:
            # Update role values
            await db.execute(text("""
                UPDATE users 
                SET role = CASE 
                    WHEN role = 'visitor' THEN 'VISITOR'
                    WHEN role = 'user' THEN 'USER'
                    WHEN role = 'admin' THEN 'ADMIN'
                    ELSE role
                END
            """))
            
            # Update auth_provider values
            await db.execute(text("""
                UPDATE users 
                SET auth_provider = CASE 
                    WHEN auth_provider = 'email' THEN 'EMAIL'
                    WHEN auth_provider = 'google' THEN 'GOOGLE'
                    WHEN auth_provider = 'username' THEN 'USERNAME'
                    ELSE auth_provider
                END
            """))
            
            await db.commit()
            print("✅ Successfully updated enum values to uppercase!")
            
            # Verify the update
            result = await db.execute(text("""
                SELECT username, role, auth_provider 
                FROM users 
                WHERE username = 'admin'
            """))
            row = result.fetchone()
            if row:
                print(f"\n✅ Admin user verified:")
                print(f"   Username: {row[0]}")
                print(f"   Role: {row[1]}")
                print(f"   Auth Provider: {row[2]}")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error updating enum values: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(update_enum_values())

