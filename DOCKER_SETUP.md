# Docker Desktop 安装和数据库设置指南

本指南将帮助你在 Windows 上安装 Docker Desktop 并设置 PostgreSQL 数据库。

## 步骤 1: 系统要求检查

### Windows 10/11 要求：
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 或更高)
- 或 Windows 11 64-bit: Home, Pro, Enterprise, or Education
- 启用 WSL 2 功能
- 启用虚拟化（在 BIOS 中）

### 检查虚拟化是否启用：

1. 按 `Ctrl + Shift + Esc` 打开任务管理器
2. 点击 "性能" 标签
3. 选择 "CPU"
4. 查看 "虚拟化" 是否显示 "已启用"

如果显示 "已禁用"，需要在 BIOS 中启用（重启电脑，按 F2/F10/Del 进入 BIOS）。

## 步骤 2: 安装 WSL 2

打开 PowerShell（管理员权限）：

```powershell
# 启用 WSL
wsl --install

# 或者如果已安装，更新到 WSL 2
wsl --set-default-version 2
```

重启电脑。

## 步骤 3: 下载 Docker Desktop

1. 访问 https://www.docker.com/products/docker-desktop/
2. 点击 "Download for Windows"
3. 下载 `Docker Desktop Installer.exe`（约 500MB）

## 步骤 4: 安装 Docker Desktop

1. 运行 `Docker Desktop Installer.exe`
2. 确保勾选 "Use WSL 2 instead of Hyper-V"
3. 点击 "Ok" 开始安装
4. 安装完成后，点击 "Close and restart"
5. 重启电脑

## 步骤 5: 启动 Docker Desktop

1. 从开始菜单启动 "Docker Desktop"
2. 接受服务条款
3. 可以跳过登录（点击 "Continue without signing in"）
4. 等待 Docker Engine 启动（右下角图标变为绿色）

## 步骤 6: 验证 Docker 安装

打开 PowerShell 或命令提示符：

```powershell
# 检查 Docker 版本
docker --version

# 应该看到类似输出：
# Docker version 24.0.x, build xxxxx

# 运行测试容器
docker run hello-world

# 应该看到 "Hello from Docker!" 消息
```

## 步骤 7: 启动 PostgreSQL 容器

在 PowerShell 中运行：

```powershell
# 启动 PostgreSQL 14 容器
docker run --name newsdb `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  -d postgres:14

# 检查容器是否运行
docker ps

# 应该看到 newsdb 容器在运行
```

## 步骤 8: 创建数据库

```powershell
# 创建数据库
docker exec -it newsdb psql -U postgres -c "CREATE DATABASE newsdb;"

# 应该看到：CREATE DATABASE

# 连接到数据库并启用扩展
docker exec -it newsdb psql -U postgres -d newsdb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 应该看到：CREATE EXTENSION
```

## 步骤 9: 运行数据库迁移

```powershell
# 进入 backend 目录
cd backend

# 激活虚拟环境
.\venv\Scripts\activate.ps1

# 运行迁移
alembic upgrade head
```

你应该看到：
```
INFO  [alembic.runtime.migration] Running upgrade  -> 3876dc2f9847, Initial schema with 5 tables
```

## 步骤 10: 验证数据库表

```powershell
# 连接到数据库
docker exec -it newsdb psql -U postgres -d newsdb

# 在 psql 中：
\dt

# 应该看到以下表：
# articles
# appointments
# chat_messages
# faqs
# article_embeddings
# alembic_version

# 查看 articles 表结构
\d articles

# 退出 psql
\q
```

## 步骤 11: 测试 API

```powershell
# 确保服务器正在运行
# 如果没有运行，启动它：
uvicorn app.main:app --reload

# 在新终端中运行测试
python test_auth.py
python test_articles.py
```

## Docker 常用命令

### 容器管理

```powershell
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 启动容器
docker start newsdb

# 停止容器
docker stop newsdb

# 重启容器
docker restart newsdb

# 删除容器
docker rm newsdb

# 删除容器和数据（谨慎！）
docker rm -f newsdb
```

### 日志和调试

```powershell
# 查看容器日志
docker logs newsdb

# 实时查看日志
docker logs -f newsdb

# 进入容器 shell
docker exec -it newsdb bash

# 在容器中运行 psql
docker exec -it newsdb psql -U postgres -d newsdb
```

### 数据备份和恢复

```powershell
# 备份数据库
docker exec newsdb pg_dump -U postgres newsdb > backup.sql

# 恢复数据库
docker exec -i newsdb psql -U postgres newsdb < backup.sql
```

## 常见问题

### Q1: Docker Desktop 无法启动

**错误**: "Docker Desktop starting..." 一直卡住

**解决方案**:
1. 确保 WSL 2 已安装：`wsl --list --verbose`
2. 重启 Docker Desktop
3. 重启电脑
4. 检查 Windows 更新

### Q2: 端口 5432 已被占用

**错误**: `port is already allocated`

**解决方案**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5432

# 停止占用端口的服务
# 或使用不同端口：
docker run --name newsdb -e POSTGRES_PASSWORD=postgres -p 5433:5432 -d postgres:14

# 然后更新 .env 中的端口号
```

### Q3: 容器启动失败

**错误**: Container exits immediately

**解决方案**:
```powershell
# 查看容器日志
docker logs newsdb

# 删除并重新创建容器
docker rm -f newsdb
docker run --name newsdb -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14
```

### Q4: 无法连接到数据库

**错误**: `Connection refused`

**解决方案**:
1. 确保容器正在运行：`docker ps`
2. 检查 `.env` 文件中的连接字符串
3. 确保使用 `localhost` 而不是 `127.0.0.1`

### Q5: WSL 2 安装失败

**解决方案**:
```powershell
# 手动启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启电脑

# 下载并安装 WSL 2 内核更新包
# https://aka.ms/wsl2kernel

# 设置 WSL 2 为默认版本
wsl --set-default-version 2
```

## Docker Desktop 设置优化

### 资源限制

1. 打开 Docker Desktop
2. 点击右上角齿轮图标（Settings）
3. 选择 "Resources"
4. 调整：
   - **CPUs**: 2-4 个（根据你的 CPU）
   - **Memory**: 4-8 GB（根据你的内存）
   - **Disk**: 20-50 GB

### 自动启动

1. Settings > General
2. 勾选 "Start Docker Desktop when you log in"

## 数据持久化

默认情况下，Docker 容器的数据存储在 Docker 卷中。如果删除容器，数据会丢失。

### 使用命名卷（推荐）

```powershell
# 创建命名卷
docker volume create newsdb_data

# 使用卷启动容器
docker run --name newsdb `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  -v newsdb_data:/var/lib/postgresql/data `
  -d postgres:14
```

### 使用本地目录

```powershell
# 使用本地目录存储数据
docker run --name newsdb `
  -e POSTGRES_PASSWORD=postgres `
  -p 5432:5432 `
  -v D:\postgres-data:/var/lib/postgresql/data `
  -d postgres:14
```

## 下一步

数据库设置完成后：

1. ✅ 运行测试验证所有功能
2. ✅ 开始开发前端集成
3. ✅ 实现剩余的 API（预约、聊天、FAQ）

## 卸载

如果需要完全卸载：

```powershell
# 1. 停止并删除所有容器
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# 2. 删除所有镜像
docker rmi $(docker images -q)

# 3. 删除所有卷
docker volume rm $(docker volume ls -q)

# 4. 卸载 Docker Desktop
# 从 Windows 设置 > 应用 > Docker Desktop > 卸载
```

## 资源链接

- Docker Desktop 文档: https://docs.docker.com/desktop/
- PostgreSQL Docker 镜像: https://hub.docker.com/_/postgres
- WSL 2 文档: https://docs.microsoft.com/en-us/windows/wsl/

