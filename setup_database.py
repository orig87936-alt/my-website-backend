"""
自动数据库设置脚本
支持 PostgreSQL 和 SQLite（临时方案）
"""
import os
import sys
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_success(text):
    """打印成功消息"""
    print(f"✅ {text}")

def print_error(text):
    """打印错误消息"""
    print(f"❌ {text}")

def print_warning(text):
    """打印警告消息"""
    print(f"⚠️  {text}")

def print_info(text):
    """打印信息"""
    print(f"ℹ️  {text}")

def check_postgresql():
    """检查 PostgreSQL 是否可用"""
    try:
        import asyncpg
        from app.config import get_settings
        import asyncio
        
        settings = get_settings()
        
        async def test_connection():
            try:
                # 尝试连接数据库
                conn = await asyncpg.connect(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
                await conn.close()
                return True
            except Exception as e:
                return False
        
        return asyncio.run(test_connection())
    except Exception as e:
        return False

def create_sqlite_env():
    """创建 SQLite 配置"""
    env_path = Path(".env")
    
    # 读取现有 .env
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        with open(".env.example", 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # 替换 DATABASE_URL
    new_lines = []
    for line in lines:
        if line.startswith('DATABASE_URL='):
            new_lines.append('DATABASE_URL=sqlite+aiosqlite:///./newsdb.sqlite\n')
            new_lines.append('# 原始 PostgreSQL URL (已注释):\n')
            new_lines.append(f'# {line}')
        else:
            new_lines.append(line)
    
    # 写入 .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print_success("已更新 .env 文件使用 SQLite")

def install_sqlite_driver():
    """安装 SQLite 驱动"""
    import subprocess
    
    print_info("正在安装 aiosqlite...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "aiosqlite"], 
                      check=True, capture_output=True)
        print_success("aiosqlite 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"安装失败: {e}")
        return False

def update_database_config():
    """更新数据库配置以支持 SQLite"""
    database_py = Path("app/database.py")
    
    content = database_py.read_text(encoding='utf-8')
    
    # 检查是否已经支持 SQLite
    if 'sqlite' in content.lower():
        print_info("database.py 已支持 SQLite")
        return
    
    # 添加 SQLite 支持
    new_content = content.replace(
        'from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker',
        'from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker\nimport re'
    )
    
    new_content = new_content.replace(
        'engine = create_async_engine(',
        '''# 检查是否使用 SQLite
is_sqlite = 'sqlite' in settings.DATABASE_URL

# 创建引擎配置
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
}

if not is_sqlite:
    # PostgreSQL 配置
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    })
else:
    # SQLite 配置
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
    })

engine = create_async_engine('''
    )
    
    new_content = new_content.replace(
        '    settings.DATABASE_URL,\n    echo=settings.ENVIRONMENT == "development",\n    pool_size=10,\n    max_overflow=20,\n    pool_recycle=3600,\n)',
        '    settings.DATABASE_URL,\n    **engine_kwargs\n)'
    )
    
    database_py.write_text(new_content, encoding='utf-8')
    print_success("已更新 database.py 支持 SQLite")

def create_sqlite_migration():
    """创建 SQLite 兼容的迁移"""
    print_info("创建 SQLite 兼容的数据库表...")
    
    # 创建简化的迁移脚本
    migration_script = '''"""
SQLite 临时迁移脚本
"""
from sqlalchemy import create_engine, text
from app.models.base import Base
from app.models.article import Article
from app.models.appointment import Appointment
from app.models.chat import ChatMessage
from app.models.faq import FAQ
# 注意：SQLite 不支持 pgvector，跳过 ArticleEmbedding

def run_migration():
    """运行迁移"""
    engine = create_engine('sqlite:///./newsdb.sqlite')
    
    # 创建所有表（除了 article_embeddings）
    Base.metadata.create_all(engine, tables=[
        Article.__table__,
        Appointment.__table__,
        ChatMessage.__table__,
        FAQ.__table__,
    ])
    
    print("✅ SQLite 数据库表创建成功")
    print("⚠️  注意：article_embeddings 表未创建（SQLite 不支持向量类型）")

if __name__ == "__main__":
    run_migration()
'''
    
    Path("migrate_sqlite.py").write_text(migration_script, encoding='utf-8')
    print_success("已创建 migrate_sqlite.py")

def main():
    """主函数"""
    print_header("数据库自动设置向导")
    
    print_info("检查数据库连接...")
    
    # 检查 PostgreSQL
    if check_postgresql():
        print_success("PostgreSQL 数据库连接成功！")
        print_info("你可以直接运行: alembic upgrade head")
        return
    
    print_warning("无法连接到 PostgreSQL 数据库")
    print()
    
    # 提供选项
    print("请选择:")
    print("1. 使用 Supabase 在线数据库（推荐，5分钟设置）")
    print("2. 使用 SQLite 临时数据库（立即可用，但功能受限）")
    print("3. 退出，我自己安装 PostgreSQL")
    print()
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        print_header("Supabase 设置指南")
        print("1. 访问 https://supabase.com/ 并注册")
        print("2. 创建新项目（选择离你最近的区域）")
        print("3. 在 Settings > Database 中找到连接字符串")
        print("4. 复制 URI 格式的连接字符串")
        print("5. 将 postgresql:// 改为 postgresql+asyncpg://")
        print("6. 更新 .env 文件中的 DATABASE_URL")
        print("7. 在 SQL Editor 中运行: CREATE EXTENSION IF NOT EXISTS vector;")
        print("8. 运行: alembic upgrade head")
        print()
        print_info("详细步骤请查看: QUICK_START_SUPABASE.md")
        
    elif choice == "2":
        print_header("设置 SQLite 临时数据库")
        
        # 安装驱动
        if not install_sqlite_driver():
            print_error("安装失败，请手动运行: pip install aiosqlite")
            return
        
        # 更新配置
        create_sqlite_env()
        update_database_config()
        create_sqlite_migration()
        
        print()
        print_success("SQLite 设置完成！")
        print()
        print_info("现在运行: python migrate_sqlite.py")
        print()
        print_warning("注意事项:")
        print("  - SQLite 不支持向量搜索（AI 聊天功能受限）")
        print("  - 不支持某些 PostgreSQL 特性")
        print("  - 仅用于开发测试")
        print("  - 生产环境必须使用 PostgreSQL")
        print()
        print_info("稍后可以迁移到 PostgreSQL，数据不会丢失")
        
    else:
        print_info("好的，请参考以下文档安装 PostgreSQL:")
        print("  - Docker 方式: DOCKER_SETUP.md")
        print("  - 本地安装: DATABASE_SETUP.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消")
    except Exception as e:
        print_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

