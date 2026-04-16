# 🐳 Docker 部署指南

## 快速开始

### 1. 环境准备

确保已安装：
- Docker
- Docker Compose

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置你的 Bot Token
nano .env
```

`.env` 文件示例：
```env
BOT_TOKEN=your_bot_token_here
SPAM_THRESHOLD=0.95
MAX_VIOLATIONS=3
LOG_LEVEL=INFO
```

### 3. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 常用命令

### 查看日志
```bash
# 实时查看日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100

# 查看特定时间段的日志
docker-compose logs --since=1h
```

### 管理容器
```bash
# 重启服务
docker-compose restart

# 重建并启动（代码更新后）
docker-compose up -d --build

# 进入容器内部
docker-compose exec spam-bot bash

# 查看容器状态
docker-compose ps
```

### 数据备份
```bash
# 备份数据库和模型
tar -czvf backup-$(date +%Y%m%d).tar.gz data/ logs/

# 恢复数据
tar -xzvf backup-20240101.tar.gz
```

## 高级配置

### 使用外部数据库

如果使用PostgreSQL等外部数据库，修改 `docker-compose.yml`：

```yaml
services:
  spam-bot:
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/spambot
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=spambot
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 多实例部署

如果需要部署多个机器人实例：

```yaml
version: '3.8'

services:
  spam-bot-1:
    build: .
    container_name: spam-bot-1
    environment:
      - BOT_TOKEN=${BOT_TOKEN_1}
    volumes:
      - ./data/bot1:/app/data
      - ./logs/bot1:/app/logs

  spam-bot-2:
    build: .
    container_name: spam-bot-2
    environment:
      - BOT_TOKEN=${BOT_TOKEN_2}
    volumes:
      - ./data/bot2:/app/data
      - ./logs/bot2:/app/logs
```

### 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务
docker stack deploy -c docker-compose.yml spam-bot

# 查看服务状态
docker service ls

# 扩容
docker service scale spam-bot_spam-bot=3
```

## 故障排查

### 容器无法启动
```bash
# 检查日志
docker-compose logs

# 检查环境变量
docker-compose config

# 手动运行查看错误
docker-compose run --rm spam-bot python start.py
```

### 权限问题
```bash
# 修复数据目录权限
sudo chown -R 1000:1000 data/ logs/

# 或使用 Docker 用户
user: "1000:1000"
```

### 网络问题
```bash
# 检查网络连接
docker-compose exec spam-bot curl -I https://api.telegram.org

# 查看网络配置
docker network ls
docker network inspect spam-bot_default
```

## 更新部署

### 更新代码
```bash
# 拉取最新代码
git pull

# 重建并重启
docker-compose up -d --build

# 清理旧镜像
docker image prune -f
```

### 更新配置
```bash
# 修改 .env 文件后重启
docker-compose restart
```

## 安全建议

1. **保护 Bot Token**：不要将 `.env` 文件提交到版本控制
2. **数据备份**：定期备份 `data/` 目录
3. **日志轮转**：日志会自动轮转，无需手动清理
4. **网络隔离**：使用 Docker 网络隔离服务

## 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  spam-bot:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## 监控

### 使用 Prometheus + Grafana

添加监控导出器：

```yaml
services:
  spam-bot:
    # ... 原有配置
    
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 生产环境建议

1. **使用反向代理**：Nginx 或 Traefik
2. **SSL/TLS**：Let's Encrypt 自动证书
3. **自动重启**：配置 `restart: always` 或 `unless-stopped`
4. **日志收集**：使用 ELK 或 Loki
5. **告警通知**：配置健康检查失败告警
