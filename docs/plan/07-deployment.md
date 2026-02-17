# 第七章：部署方案

## 目标环境

- **服务器**：serverop（SSH: `adminc@serverop`）
- **部署方式**：Docker Compose
- **Git 仓库**：`adminc@serverop:~/repos/bago.git`
- **分支**：master

## Docker Compose 架构

```yaml
services:
  nginx:       # 反向代理 + SSL
  api:         # FastAPI 后端
  web:         # Next.js 前端
  db:          # PostgreSQL
  redis:       # Redis
```

## 容器配置

### bago-nginx

- 镜像：nginx:alpine
- 端口：80, 443
- 职责：路由分发、SSL 终止、静态资源缓存
- 路由规则：
  - `/api/*` → bago-api:8000
  - `/*` → bago-web:3000

### bago-api

- 基础镜像：python:3.12-slim
- 端口：8000（仅内部）
- 启动命令：`uvicorn app.main:app --host 0.0.0.0 --port 8000`
- 环境变量：
  - `DATABASE_URL`
  - `REDIS_URL`
  - `JWT_SECRET`

### bago-web

- 基础镜像：node:20-alpine
- 端口：3000（仅内部）
- 构建：`npm run build && npm start`
- 环境变量：
  - `API_BASE_URL=http://api:8000`

### bago-db

- 镜像：postgres:16-alpine
- 端口：5432（仅内部）
- 数据卷：`bago-pgdata:/var/lib/postgresql/data`

### bago-redis

- 镜像：redis:7-alpine
- 端口：6379（仅内部）

## 部署流程

```
本地开发
  ↓
git push serverop master
  ↓
SSH 到 serverop
  ↓
docker compose build && docker compose up -d
  ↓
运行数据库迁移: docker compose exec api alembic upgrade head
  ↓
验证服务状态: docker compose ps
```

## 数据持久化

- PostgreSQL 数据：Docker Volume `bago-pgdata`
- Redis 数据：不持久化（纯缓存，丢失可恢复）
- 上传文件（如果有）：Docker Volume `bago-uploads`

## 监控

MVP 阶段保持简单：
- `docker compose logs -f` 查看日志
- FastAPI 内置 `/docs` 端点可查看 API 状态
- 后续可加 Prometheus + Grafana
