"""
Check admin user role in database
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole


async def check_admin():
    """Check admin user role"""
    async with AsyncSessionLocal() as db:
        # Find admin user
        result = await db.execute(
            select(User).where(User.username == 'admin')
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("❌ Admin user not found!")
            return
        
        print("✅ Admin user found:")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Display Name: {admin.display_name}")
        print(f"   Role: {admin.role} (type: {type(admin.role)})")
        print(f"   Role value: {admin.role.value if hasattr(admin.role, 'value') else admin.role}")
        print(f"   Auth Provider: {admin.auth_provider}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Is Verified: {admin.is_verified}")
        print()
        print(f"   Expected role: {UserRole.ADMIN} (type: {type(UserRole.ADMIN)})")
        print(f"   Expected role value: {UserRole.ADMIN.value}")
        print()
        print(f"   Role matches ADMIN? {admin.role == UserRole.ADMIN}")
        print(f"   Role value matches 'admin'? {admin.role.value == 'admin' if hasattr(admin.role, 'value') else admin.role == 'admin'}")


if __name__ == "__main__":
    asyncio.run(check_admin())

