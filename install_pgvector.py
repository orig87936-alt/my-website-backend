"""
在 AWS RDS PostgreSQL 数据库中安装 pgvector 扩展
"""
import asyncpg
import asyncio


async def install_pgvector():
    """安装 pgvector 扩展"""
    print("🔄 正在连接到 AWS RDS PostgreSQL...")
    print("-" * 60)
    
    # 数据库连接信息
    db_config = {
        'host': 'sl-news-db.czks6o22ep09.us-east-2.rds.amazonaws.com',
        'port': 5432,
        'user': 'postgres',
        'password': 'Slnews2024!',
        'database': 'slnews'  # 连接到你的数据库
    }
    
    try:
        # 连接到数据库
        conn = await asyncpg.connect(**db_config)
        
        print("✅ 已连接到数据库: slnews")
        print("-" * 60)
        
        # 检查 pgvector 扩展是否已安装
        print("🔍 检查 pgvector 扩展状态...")
        installed = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector'")
        
        if installed:
            print("✅ pgvector 扩展已经安装！")
            version = installed[0]['extversion']
            print(f"   版本: {version}")
        else:
            print("⚠️  pgvector 扩展未安装，正在安装...")
            
            # 安装 pgvector 扩展
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            print("✅ pgvector 扩展安装成功！")
            
            # 验证安装
            installed = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if installed:
                version = installed[0]['extversion']
                print(f"   版本: {version}")
        
        print("-" * 60)
        
        # 测试 pgvector 功能
        print("🧪 测试 pgvector 功能...")
        
        # 创建测试表
        await conn.execute("""
            DROP TABLE IF EXISTS test_vectors;
            CREATE TABLE test_vectors (
                id SERIAL PRIMARY KEY,
                embedding vector(3)
            );
        """)
        print("   ✅ 创建测试表成功")
        
        # 插入测试数据
        await conn.execute("""
            INSERT INTO test_vectors (embedding) VALUES 
            ('[1,2,3]'),
            ('[4,5,6]');
        """)
        print("   ✅ 插入测试数据成功")
        
        # 查询测试数据
        result = await conn.fetch("SELECT * FROM test_vectors")
        print(f"   ✅ 查询测试数据成功（{len(result)} 条记录）")
        
        # 删除测试表
        await conn.execute("DROP TABLE test_vectors")
        print("   ✅ 清理测试数据成功")
        
        print("-" * 60)
        print("✅ pgvector 扩展已安装并测试通过！")
        print("-" * 60)
        
        # 关闭连接
        await conn.close()
        print("🔒 连接已关闭")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败：{type(e).__name__}")
        print(f"   错误详情: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 安装 pgvector 扩展")
    print("=" * 60)
    print()
    
    # 运行安装
    success = asyncio.run(install_pgvector())
    
    print()
    if success:
        print("🎉 pgvector 扩展安装完成！")
        print("📝 数据库配置信息：")
        print("   数据库名称: slnews")
        print("   主机: sl-news-db.czks6o22ep09.us-east-2.rds.amazonaws.com")
        print("   端口: 5432")
        print("   用户: postgres")
    else:
        print("⚠️  安装失败，请检查错误信息。")
    print("=" * 60)

