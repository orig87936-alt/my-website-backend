# 数据库设置指南

本文档介绍如何设置 PostgreSQL 数据库以运行 News Platform API。

## 选项 1: 使用 Docker (推荐)

### 1.1 安装 Docker

如果还没有安装 Docker，请访问 [Docker 官网](https://www.docker.com/get-started) 下载并安装。

### 1.2 启动 PostgreSQL 容器

```bash
# 启动 PostgreSQL 14 容器
docker run --name newsdb \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:14

# Windows PowerShell 版本
docker run --name newsdb `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  -d postgres:14
```

### 1.3 创建数据库

```bash
# 创建数据库
docker exec -it newsdb psql -U postgres -c "CREATE DATABASE newsdb;"

# 连接到数据库
docker exec -it newsdb psql -U postgres -d newsdb

# 在 psql 中启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

# 退出 psql
\q
```

### 1.4 运行数据库迁移

```bash
# 进入 backend 目录
cd backend

# 激活虚拟环境
.\venv\Scripts\activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# 运行迁移
alembic upgrade head
```

### 1.5 验证数据库

```bash
# 连接到数据库
docker exec -it newsdb psql -U postgres -d newsdb

# 查看所有表
\dt

# 应该看到以下表：
# - articles
# - appointments
# - chat_messages
# - faqs
# - article_embeddings
# - alembic_version

# 查看 articles 表结构
\d articles

# 退出
\q
```

## 选项 2: 本地安装 PostgreSQL

### 2.1 安装 PostgreSQL

#### Windows
1. 下载 [PostgreSQL 14](https://www.postgresql.org/download/windows/)
2. 运行安装程序
3. 记住设置的密码（默认用户是 `postgres`）
4. 确保安装了 pgAdmin 4（可选，用于图形化管理）

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql-14 postgresql-contrib-14
```

#### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

### 2.2 安装 pgvector 扩展

#### 从源码编译 (Linux/macOS)
```bash
# 克隆 pgvector 仓库
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# 编译并安装
make
sudo make install
```

#### Windows
下载预编译的 pgvector DLL 文件并放到 PostgreSQL 的 `lib` 目录。

### 2.3 创建数据库

```bash
# 使用 psql 连接
psql -U postgres

# 创建数据库
CREATE DATABASE newsdb;

# 连接到新数据库
\c newsdb

# 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

# 退出
\q
```

### 2.4 更新 .env 文件

确保 `.env` 文件中的数据库连接字符串正确：

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/newsdb
```

### 2.5 运行迁移

```bash
cd backend
.\venv\Scripts\activate.ps1  # Windows
alembic upgrade head
```

## 选项 3: 使用云数据库 (AWS RDS)

### 3.1 创建 RDS 实例

1. 登录 AWS 控制台
2. 进入 RDS 服务
3. 点击 "Create database"
4. 选择 PostgreSQL 14
5. 选择实例类型（开发环境可选 db.t3.micro）
6. 设置数据库名称、用户名和密码
7. 配置安全组，允许你的 IP 访问端口 5432

### 3.2 安装 pgvector

连接到 RDS 实例后：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

注意：某些 RDS 配置可能不支持 pgvector，需要使用自定义参数组。

### 3.3 更新 .env 文件

```env
DATABASE_URL=postgresql+asyncpg://username:password@your-rds-endpoint.rds.amazonaws.com:5432/newsdb
```

### 3.4 运行迁移

```bash
cd backend
.\venv\Scripts\activate.ps1
alembic upgrade head
```

## 常见问题

### Q1: 连接被拒绝 (Connection refused)

**错误**: `OSError: [Errno 10061] Connect call failed`

**解决方案**:
1. 确保 PostgreSQL 正在运行
   ```bash
   # Docker
   docker ps | grep newsdb
   
   # 本地安装 (Windows)
   services.msc  # 查找 postgresql-x64-14
   
   # 本地安装 (Linux)
   sudo systemctl status postgresql
   ```

2. 检查端口 5432 是否被占用
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```

### Q2: 数据库不存在

**错误**: `database "newsdb" does not exist`

**解决方案**:
```bash
# Docker
docker exec -it newsdb psql -U postgres -c "CREATE DATABASE newsdb;"

# 本地
psql -U postgres -c "CREATE DATABASE newsdb;"
```

### Q3: pgvector 扩展不可用

**错误**: `extension "vector" is not available`

**解决方案**:
1. 确保已安装 pgvector 扩展
2. 重启 PostgreSQL 服务
3. 检查 PostgreSQL 版本（需要 11+）

### Q4: 迁移失败

**错误**: `alembic.util.exc.CommandError`

**解决方案**:
```bash
# 检查当前迁移状态
alembic current

# 查看迁移历史
alembic history

# 回滚到初始状态
alembic downgrade base

# 重新运行迁移
alembic upgrade head
```

### Q5: 权限错误

**错误**: `permission denied for database`

**解决方案**:
```sql
-- 授予用户权限
GRANT ALL PRIVILEGES ON DATABASE newsdb TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

## 数据库管理工具

### pgAdmin 4
- 图形化界面
- 支持 Windows/Linux/macOS
- 下载: https://www.pgadmin.org/

### DBeaver
- 跨平台数据库管理工具
- 支持多种数据库
- 下载: https://dbeaver.io/

### TablePlus
- 现代化界面
- macOS/Windows/Linux
- 下载: https://tableplus.com/

## 备份和恢复

### 备份数据库

```bash
# Docker
docker exec newsdb pg_dump -U postgres newsdb > backup.sql

# 本地
pg_dump -U postgres newsdb > backup.sql
```

### 恢复数据库

```bash
# Docker
docker exec -i newsdb psql -U postgres newsdb < backup.sql

# 本地
psql -U postgres newsdb < backup.sql
```

## 性能优化

### 1. 连接池配置

在 `app/database.py` 中已配置：
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 最大溢出连接数
    pool_recycle=3600      # 连接回收时间（秒）
)
```

### 2. 索引优化

所有必要的索引已在迁移文件中创建：
- 文章：category + published_at 复合索引
- 预约：唯一时间槽索引（排除已取消）
- FAQ：GIN 索引（关键词数组）
- 向量嵌入：HNSW 索引（余弦相似度）

### 3. 查询优化

- 使用 `select()` 而不是 `query()`（SQLAlchemy 2.0 风格）
- 使用 `limit()` 和 `offset()` 进行分页
- 使用 `where()` 过滤而不是 Python 过滤
- 使用 `func.count()` 而不是 `len()`

## 下一步

数据库设置完成后，可以：

1. 启动 API 服务器
   ```bash
   uvicorn app.main:app --reload
   ```

2. 运行测试
   ```bash
   python test_auth.py
   python test_articles.py
   ```

3. 访问 API 文档
   - http://localhost:8000/api/docs
   - http://localhost:8000/api/redoc

4. 开始开发前端集成

