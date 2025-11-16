"""验证数据库表"""
import sqlite3

conn = sqlite3.connect('newsdb.sqlite')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n" + "="*60)
print("✅ 数据库验证")
print("="*60)
print(f"\n数据库文件: newsdb.sqlite")
print(f"\n已创建的表 ({len(tables)} 个):")
for table in tables:
    table_name = table[0]
    print(f"\n  📋 {table_name}")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"     列数: {len(columns)}")
    
    # 获取行数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"     数据行数: {count}")

conn.close()

print("\n" + "="*60)
print("✅ 数据库验证完成")
print("="*60)
print("\n下一步:")
print("  1. 运行测试: python test_auth.py")
print("  2. 运行测试: python test_articles.py")
print()

