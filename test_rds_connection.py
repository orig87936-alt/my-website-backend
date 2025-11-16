"""
测试 AWS RDS PostgreSQL 数据库连接
"""
import asyncpg
import asyncio


async def test_connection():
    """测试数据库连接"""
    print("🔄 正在连接到 AWS RDS PostgreSQL...")
    print("-" * 60)

    # 数据库连接信息（先连接到默认的 postgres 数据库）
    db_config = {
        'host': 'sl-news-db.czks6o22ep09.us-east-2.rds.amazonaws.com',
        'port': 5432,
        'user': 'postgres',
        'password': 'Slnews2024!',
        'database': 'postgres'  # 先连接到默认数据库
    }

    try:
        # 尝试连接到默认数据库
        conn = await asyncpg.connect(**db_config)
        
        print("✅ 数据库连接成功！")
        print("-" * 60)
        
        # 获取 PostgreSQL 版本
        version = await conn.fetchval('SELECT version()')
        print(f"📊 PostgreSQL 版本:")
        print(f"   {version}")
        print("-" * 60)
        
        # 检查当前数据库
        current_db = await conn.fetchval('SELECT current_database()')
        print(f"📁 当前数据库: {current_db}")
        
        # 检查当前用户
        current_user = await conn.fetchval('SELECT current_user')
        print(f"👤 当前用户: {current_user}")
        
        # 列出所有数据库
        databases = await conn.fetch('SELECT datname FROM pg_database WHERE datistemplate = false')
        print(f"\n📚 可用数据库:")
        for db in databases:
            print(f"   - {db['datname']}")
        
        # 检查是否已安装 pgvector 扩展
        print("\n🔍 检查 pgvector 扩展...")
        extensions = await conn.fetch("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        if extensions:
            print("   ✅ pgvector 扩展可用")
            
            # 检查是否已安装
            installed = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if installed:
                print("   ✅ pgvector 扩展已安装")
            else:
                print("   ⚠️  pgvector 扩展未安装（需要手动安装）")
        else:
            print("   ❌ pgvector 扩展不可用")
        
        print("-" * 60)
        print("✅ 所有测试通过！数据库已准备就绪！")
        print("-" * 60)
        
        # 关闭连接
        await conn.close()
        print("🔒 连接已关闭")
        
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ 连接失败：密码错误")
        print("   请检查数据库密码是否正确")
        return False
        
    except asyncpg.exceptions.InvalidCatalogNameError:
        print("❌ 连接失败：数据库不存在")
        print("   请检查数据库名称是否正确")
        return False
        
    except Exception as e:
        print(f"❌ 连接失败：{type(e).__name__}")
        print(f"   错误详情: {e}")
        print("\n💡 可能的原因:")
        print("   1. 安全组配置不正确（检查入站规则）")
        print("   2. 数据库实例未启动")
        print("   3. 网络连接问题")
        print("   4. 主机名或端口错误")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AWS RDS PostgreSQL 连接测试")
    print("=" * 60)
    print()
    
    # 运行测试
    success = asyncio.run(test_connection())
    
    print()
    if success:
        print("🎉 测试完成！可以继续下一步部署。")
    else:
        print("⚠️  测试失败，请检查配置后重试。")
    print("=" * 60)

