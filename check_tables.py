import asyncio
import asyncpg

async def check_tables():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='newsuser',
        password='newspass123',
        database='newsdb'
    )
    
    # 查询所有表
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    print("📊 当前数据库中的表：")
    print("=" * 50)
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table['table_name']}")
    
    print("\n" + "=" * 50)
    print(f"总计: {len(tables)} 个表")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tables())

