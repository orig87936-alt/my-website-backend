# S&L News Backend API

FastAPI 后端服务，提供新闻管理、预约系统和智能问答功能。

## 技术栈

- **框架**: FastAPI 0.109.0
- **数据库**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **AI**: DeepSeek API
- **部署**: AWS EC2 + RDS

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
.\venv\Scripts\Activate.ps1

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入实际配置
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 3. 数据库设置

```bash
# 确保 PostgreSQL 已安装并运行
# 创建数据库
createdb sl_news

# 或使用 psql
psql -U postgres
CREATE DATABASE sl_news;
\q

# 运行数据库迁移（稍后配置）
alembic upgrade head
```

### 4. 启动开发服务器

```bash
# 方式 1：使用 uvicorn 直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2：使用 Python 模块运行
python -m uvicorn app.main:app --reload
```

访问：
- API 文档: http://localhost:8000/api/docs
- ReDoc 文档: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

### 5. 测试 API

```bash
# 运行认证测试
python test_auth.py

# 测试登录 (使用 curl)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 模型
│   ├── api/                 # API 路由
│   ├── services/            # 业务逻辑
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
├── requirements.txt         # Python 依赖
├── .env                     # 环境变量（不提交）
├── .env.example             # 环境变量模板
└── README.md
```

## API 端点（规划）

### 文章管理
- `GET /api/v1/articles` - 获取文章列表
- `GET /api/v1/articles/{id}` - 获取单篇文章
- `POST /api/v1/articles` - 创建文章（需要认证）
- `PUT /api/v1/articles/{id}` - 更新文章（需要认证）
- `DELETE /api/v1/articles/{id}` - 删除文章（需要认证）

### 预约管理
- `POST /api/v1/appointments` - 创建预约
- `GET /api/v1/appointments` - 获取预约列表（需要认证）
- `GET /api/v1/appointments/available-slots` - 获取可用时间槽

### 智能问答
- `POST /api/v1/chat` - 发送消息

### 认证
- `POST /api/v1/auth/login` - 管理员登录
- `POST /api/v1/auth/verify` - 验证 Token

## 开发进度

### 已完成 ✅
- [x] Phase 1: 项目初始化
  - 目录结构、虚拟环境、依赖安装
- [x] Phase 2: 数据库模型
  - 5个模型：Article, Appointment, ChatMessage, FAQ, ArticleEmbedding
  - Alembic 迁移配置
  - 初始迁移文件生成
- [x] Phase 3: 认证与安全
  - JWT 认证系统
  - 密码哈希 (argon2)
  - 管理员登录 API
  - 权限依赖注入

### 进行中 🚧
- [ ] Phase 4: 文章管理 API (T024-T035)
- [ ] Phase 5: 预约系统 API (T036-T044)
- [ ] Phase 6: AI 聊天 API (T045-T058)
- [ ] Phase 7: FAQ 管理 API (T059-T082)
- [ ] Phase 8: 集成与优化 (T083-T095)

### 测试状态
```
✅ 认证 API 测试通过
✅ 服务器成功启动
✅ API 文档可访问: http://localhost:8000/api/docs
```

详细进度查看: [IMPLEMENTATION_PROGRESS.md](./IMPLEMENTATION_PROGRESS.md)

## 部署

### AWS EC2 部署步骤

1. 创建 EC2 实例（Ubuntu 22.04）
2. 安装 Python 3.11+
3. 克隆代码并安装依赖
4. 配置 Nginx 反向代理
5. 使用 Systemd 管理服务
6. 配置 SSL 证书

详细部署文档待补充。

## 许可证

Private

