# 快速开始：使用 Supabase 数据库

这是最快的开始方式，无需安装任何本地数据库软件。

## 步骤 1: 创建 Supabase 账户

1. 访问 https://supabase.com/
2. 点击 "Start your project"
3. 使用 GitHub 账户登录（或创建新账户）

## 步骤 2: 创建新项目

1. 点击 "New Project"
2. 填写项目信息：
   - **Name**: `news-platform`
   - **Database Password**: 设置一个强密码（记住这个密码！）
   - **Region**: 选择离你最近的区域（如 Northeast Asia (Tokyo)）
3. 点击 "Create new project"
4. 等待 1-2 分钟，项目创建完成

## 步骤 3: 获取数据库连接信息

1. 在项目页面，点击左侧菜单的 "Settings" (齿轮图标)
2. 点击 "Database"
3. 向下滚动到 "Connection string" 部分
4. 选择 "URI" 标签
5. 复制连接字符串，格式类似：
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```

## 步骤 4: 启用 pgvector 扩展

1. 在项目页面，点击左侧菜单的 "SQL Editor"
2. 点击 "New query"
3. 输入以下 SQL：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. 点击 "Run" 执行

## 步骤 5: 更新 .env 文件

1. 打开 `backend/.env` 文件
2. 将连接字符串转换为 asyncpg 格式：
   
   **原始格式**:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
   
   **转换为**:
   ```
   postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
   
3. 更新 `DATABASE_URL`：
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```

## 步骤 6: 运行数据库迁移

打开终端，执行：

```bash
# 进入 backend 目录
cd backend

# 激活虚拟环境
.\venv\Scripts\activate.ps1

# 运行迁移
alembic upgrade head
```

你应该看到类似输出：
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 3876dc2f9847, Initial schema with 5 tables
```

## 步骤 7: 验证数据库表

在 Supabase 控制台：

1. 点击左侧菜单的 "Table Editor"
2. 你应该看到以下表：
   - `articles`
   - `appointments`
   - `chat_messages`
   - `faqs`
   - `article_embeddings`
   - `alembic_version`

## 步骤 8: 测试 API

```bash
# 确保服务器正在运行
# 如果没有运行，启动它：
uvicorn app.main:app --reload

# 在新终端中运行测试
python test_auth.py
python test_articles.py
```

## 步骤 9: 查看数据

在 Supabase 控制台：

1. 点击 "Table Editor"
2. 选择 `articles` 表
3. 你应该看到测试创建的文章数据

## 常见问题

### Q: 连接超时

**解决方案**: 检查网络连接，确保可以访问 Supabase 服务器。

### Q: 密码错误

**解决方案**: 
1. 在 Supabase 控制台，Settings > Database
2. 点击 "Reset database password"
3. 设置新密码
4. 更新 `.env` 文件中的连接字符串

### Q: 表已存在错误

**解决方案**:
```bash
# 回滚迁移
alembic downgrade base

# 重新运行迁移
alembic upgrade head
```

### Q: pgvector 扩展不可用

**解决方案**:
在 SQL Editor 中运行：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 优点

✅ 无需本地安装  
✅ 5 分钟内开始  
✅ 免费 500MB 存储  
✅ 支持 pgvector  
✅ 自动备份  
✅ 图形化管理界面  

## 限制

⚠️ 免费版限制：
- 500MB 数据库存储
- 2GB 带宽/月
- 项目会在 1 周不活动后暂停（可以重新激活）

## 下一步

数据库设置完成后：

1. ✅ 运行测试验证所有功能
2. ✅ 开始开发前端集成
3. ✅ 实现剩余的 API（预约、聊天、FAQ）

## 生产环境建议

对于生产环境，建议：
- 升级到 Supabase Pro 计划（$25/月）
- 或使用 AWS RDS
- 或使用自托管 PostgreSQL

但对于开发和测试，免费版完全够用！

