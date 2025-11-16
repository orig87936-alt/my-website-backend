"""
SQLite 临时迁移脚本
"""
import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./newsdb.sqlite'

from sqlalchemy import create_engine, text, event
from app.models.base import Base

# 导入所有模型
from app.models.article import Article
from app.models.appointment import Appointment
from app.models.chat import ChatMessage
from app.models.faq import FAQ
# 注意：SQLite 不支持 pgvector，跳过 ArticleEmbedding

def run_migration():
    """运行迁移"""
    engine = create_engine('sqlite:///./newsdb.sqlite', echo=True)

    # 启用外键约束
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    print("正在创建数据库表...")

    # 删除所有表（如果存在）
    Base.metadata.drop_all(engine)

    # 创建所有表（除了 article_embeddings）
    Base.metadata.create_all(engine, tables=[
        Article.__table__,
        Appointment.__table__,
        ChatMessage.__table__,
        FAQ.__table__,
    ])

    print("\n" + "="*60)
    print("✅ SQLite 数据库表创建成功")
    print("="*60)
    print("\n创建的表:")
    print("  - articles (文章)")
    print("  - appointments (预约)")
    print("  - chat_messages (聊天消息)")
    print("  - faqs (常见问题)")
    print("\n⚠️  注意：article_embeddings 表未创建（SQLite 不支持向量类型）")
    print("\n数据库文件: newsdb.sqlite")
    print("\n下一步:")
    print("  1. 启动服务器: uvicorn app.main:app --reload")
    print("  2. 运行测试: python test_auth.py")
    print("  3. 运行测试: python test_articles.py")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
