"""
Reset admin password script
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password


async def reset_admin_password():
    """Reset admin password to 'admin123'"""
    async with AsyncSessionLocal() as db:
        # Find admin user
        result = await db.execute(
            select(User).where(User.username == 'admin')
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("❌ Admin user not found!")
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                hashed_password=hash_password('admin123'),
                display_name='Administrator',
                role='ADMIN',
                auth_provider='USERNAME',
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            print("✅ Admin user created successfully!")
        else:
            print(f"✅ Found admin user: {admin.email}")
            print(f"   Current role: {admin.role}")
            print(f"   Auth provider: {admin.auth_provider}")
            
            # Update password
            new_hash = hash_password('admin123')
            admin.hashed_password = new_hash
            admin.role = 'ADMIN'
            admin.auth_provider = 'USERNAME'
            admin.is_active = True
            admin.is_verified = True
            
            await db.commit()
            print("✅ Admin password reset to 'admin123'")
            print(f"   New hash: {new_hash[:50]}...")


if __name__ == "__main__":
    asyncio.run(reset_admin_password())

