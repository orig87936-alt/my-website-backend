"""
手动创建翻译和文档上传表
绕过 Alembic 的 pgvector 扩展问题
"""
import asyncio
import asyncpg
from app.config import get_settings

async def create_tables():
    settings = get_settings()
    
    # 从 DATABASE_URL 解析连接参数
    # postgresql+asyncpg://newsuser:newspass123@localhost:5432/newsdb
    db_url = settings.DATABASE_URL
    db_url = db_url.replace('postgresql+asyncpg://', '')
    
    # 解析用户名、密码、主机、端口、数据库
    auth, rest = db_url.split('@')
    user, password = auth.split(':')
    host_port, database = rest.split('/')
    host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
    
    print(f"连接到 PostgreSQL: {host}:{port}/{database}")
    
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=int(port)
        )
        
        print("✅ 成功连接到数据库")
        
        # 检查表是否已存在
        existing_tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('translation_cache', 'translation_logs', 'document_uploads')
        """)
        
        existing_table_names = [row['tablename'] for row in existing_tables]
        
        if existing_table_names:
            print(f"\n⚠️  以下表已存在: {', '.join(existing_table_names)}")
            response = input("是否删除并重新创建? (y/N): ")
            if response.lower() == 'y':
                for table_name in existing_table_names:
                    await conn.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
                    print(f"  删除表: {table_name}")
            else:
                print("取消操作")
                await conn.close()
                return
        
        # 创建 translation_cache 表
        print("\n创建 translation_cache 表...")
        await conn.execute("""
            CREATE TABLE translation_cache (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                source_text_hash VARCHAR(64) NOT NULL,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                source_lang VARCHAR(10) NOT NULL,
                target_lang VARCHAR(10) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days' NOT NULL,
                CONSTRAINT unique_translation UNIQUE (source_text_hash, source_lang, target_lang)
            )
        """)
        print("✅ translation_cache 表创建成功")
        
        # 创建索引
        await conn.execute("""
            CREATE INDEX idx_translation_cache_hash 
            ON translation_cache (source_text_hash, source_lang, target_lang)
        """)
        await conn.execute("""
            CREATE INDEX idx_translation_cache_expires 
            ON translation_cache (expires_at)
        """)
        print("✅ translation_cache 索引创建成功")
        
        # 创建 translation_logs 表
        print("\n创建 translation_logs 表...")
        await conn.execute("""
            CREATE TABLE translation_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
                field_name VARCHAR(50) NOT NULL,
                source_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                source_lang VARCHAR(10) NOT NULL,
                target_lang VARCHAR(10) NOT NULL,
                manually_edited BOOLEAN DEFAULT FALSE NOT NULL,
                edited_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            )
        """)
        print("✅ translation_logs 表创建成功")
        
        # 创建索引
        await conn.execute("""
            CREATE INDEX idx_translation_logs_article 
            ON translation_logs (article_id)
        """)
        await conn.execute("""
            CREATE INDEX idx_translation_logs_created 
            ON translation_logs (created_at)
        """)
        print("✅ translation_logs 索引创建成功")
        
        # 创建 document_uploads 表
        print("\n创建 document_uploads 表...")
        await conn.execute("""
            CREATE TABLE document_uploads (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                filename VARCHAR(255) NOT NULL,
                file_size INTEGER NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                upload_status VARCHAR(20) NOT NULL,
                parse_result JSONB,
                error_message TEXT,
                created_by VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                CONSTRAINT valid_upload_status CHECK (upload_status IN ('success', 'failed', 'processing')),
                CONSTRAINT valid_file_type CHECK (file_type IN ('md', 'docx'))
            )
        """)
        print("✅ document_uploads 表创建成功")
        
        # 创建索引
        await conn.execute("""
            CREATE INDEX idx_document_uploads_status 
            ON document_uploads (upload_status)
        """)
        await conn.execute("""
            CREATE INDEX idx_document_uploads_created 
            ON document_uploads (created_at)
        """)
        print("✅ document_uploads 索引创建成功")
        
        # 验证表创建
        print("\n验证表创建...")
        tables = await conn.fetch("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('translation_cache', 'translation_logs', 'document_uploads')
            ORDER BY tablename
        """)
        
        print("\n✅ 成功创建以下表:")
        for table in tables:
            # 获取行数
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['tablename']}")
            print(f"  📋 {table['tablename']} (0 行)")
        
        await conn.close()
        print("\n✅ 所有表创建完成！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_tables())

