"""
PostgreSQL 数据库迁移脚本
创建所有表结构
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import get_settings
from app.models.article import Article
from app.models.appointment import Appointment
from app.models.chat import ChatMessage
from app.models.faq import FAQ
# 暂时跳过 embedding 表（需要 pgvector 扩展）
# from app.models.embedding import ArticleEmbedding
from app.models.base import Base

settings = get_settings()


async def create_tables():
    """创建所有表"""
    print("=" * 60)
    print("🚀 PostgreSQL 数据库迁移")
    print("=" * 60)
    print()
    
    # 创建引擎
    print(f"📝 连接数据库: {settings.DATABASE_URL.split('@')[1]}")
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # 显示 SQL 语句
        future=True
    )
    
    try:
        # 创建所有表
        print()
        print("📊 创建表结构...")
        print()
        
        async with engine.begin() as conn:
            # 删除所有表（如果存在）
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ 已删除旧表")
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            print("✅ 已创建新表")
        
        # 验证表
        print()
        print("🔍 验证表结构...")
        print()
        
        async with engine.connect() as conn:
            # 查询所有表
            result = await conn.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
            )
            tables = result.fetchall()
            
            print(f"✅ 成功创建 {len(tables)} 个表:")
            for table in tables:
                print(f"   - {table[0]}")
        
        print()
        print("=" * 60)
        print("✅ 数据库迁移完成！")
        print("=" * 60)
        print()
        print("📌 下一步:")
        print("   1. 运行测试: python test_auth.py")
        print("   2. 运行测试: python test_articles.py")
        print("   3. 运行测试: python test_appointments.py")
        print("   4. 运行测试: python test_chat.py")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 迁移失败！")
        print("=" * 60)
        print()
        print(f"错误: {e}")
        print()
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_tables())

