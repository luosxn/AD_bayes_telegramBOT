# 🤖 贝叶斯Telegram广告拦截机器人

一个基于朴素贝叶斯算法的智能Telegram广告拦截机器人，具备自学习能力，可以通过投喂训练数据不断提升识别准确率。

## 📑 目录

- [特性](#-特性)
- [快速开始](#-快速开始)
- [使用方法](#-使用方法)
- [Docker部署](#-docker部署)
- [配置说明](#-配置说明)
- [项目结构](#-项目结构)
- [核心算法](#-核心算法)
- [模型优化](#-模型优化)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

## ✨ 特性

- 🛡️ **智能拦截** - 基于贝叶斯算法自动识别垃圾广告，置信度超过95%才会拦截
- 📚 **自主学习** - 支持投喂训练数据，模型实时更新
- 👮 **自动封禁** - 连续违规3次自动封禁用户
- 🔄 **实时更新** - 所有群组共享同一个训练模型，一处训练，全局受益
- 💾 **数据持久化** - 训练数据和模型自动保存，重启不丢失
- 🎯 **中文优化** - 使用jieba进行中文分词，针对中文广告优化
- 🤖 **自动注册命令** - 启动时自动设置命令菜单，支持自动补全
- 🐳 **Docker支持** - 提供完整的Docker部署方案

## 🚀 快速开始

### 方式一：直接运行（推荐开发测试）

#### 1. 环境要求

- Python 3.8+
- pip

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置

复制配置文件模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Bot Token：

```env
BOT_TOKEN=your_bot_token_here
```

> 获取 Bot Token：在 Telegram 中搜索 [@BotFather](https://t.me/BotFather)，创建新机器人获取 Token。

#### 4. 初始训练（可选）

运行初始训练脚本，提供一些基础样本：

```bash
python train_initial.py
```

#### 5. 启动机器人

```bash
python start.py
```

***

### 方式二：Docker部署（推荐生产环境）

#### 1. 环境准备

确保已安装：

- Docker
- Docker Compose

#### 2. 配置环境变量

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

#### 3. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### Docker常用命令

```bash
# 查看日志
docker-compose logs -f
docker-compose logs --tail=100

# 重启服务
docker-compose restart

# 重建并启动（代码更新后）
docker-compose up -d --build

# 进入容器内部
docker-compose exec spam-bot bash

# 查看容器状态
docker-compose ps

# 备份数据
tar -czvf backup-$(date +%Y%m%d).tar.gz data/ logs/
```

#### 高级Docker配置

**使用外部数据库（PostgreSQL）**

```yaml
version: '3.8'

services:
  spam-bot:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/spambot
    depends_on:
      - postgres
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
  
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

**多实例部署**

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

***

## 📖 使用方法

### 添加到群组

1. 将机器人添加到群组
2. 给予管理员权限：
   - ✅ 删除消息
   - ✅ 封禁用户
3. 机器人自动开始工作，并发送欢迎消息

### 自动功能

- **自动检测**：实时分析群组消息，置信度>95%自动删除
- **自动封禁**：连续违规3次自动封禁用户
- **自动欢迎**：被添加到群组时自动发送欢迎消息
- **命令菜单**：自动注册命令，输入`/`显示可用命令

### 可用命令

#### 管理员命令

| 命令             | 说明          | 用法                       |
| -------------- | ----------- | ------------------------ |
| `/markspam`    | 标记垃圾消息并封禁用户 | 回复垃圾消息 + `/markspam`     |
| `/listbanuser` | 查看封禁用户列表    | `/listbanuser`           |
| `/listspam`    | 查看被标记的垃圾消息  | `/listspam`              |
| `/unban`       | 解封用户        | `/unban` 或 `/unban 用户ID` |

#### 普通命令

| 命令          | 说明       | 用法                     |
| ----------- | -------- | ---------------------- |
| `/feedspam` | 投喂垃圾消息训练 | `/feedspam 文本内容` 或回复消息 |
| `/stats`    | 查看统计信息   | `/stats`               |
| `/help`     | 查看帮助     | `/help`                |
| `/start`    | 开始/欢迎信息  | `/start`               |

### 投喂训练数据

训练数据越多，识别越准确！

#### 方法1：直接投喂

```
/feedspam 这里是要训练的垃圾广告内容
```

#### 方法2：回复消息投喂

1. 找到一条垃圾消息
2. 回复该消息
3. 发送 `/feedspam`

#### 方法3：私聊投喂

可以直接私聊机器人投喂训练数据，不会影响任何群组。

### 最佳实践

1. **初期训练**：机器人刚部署时积极使用 `/markspam` 标记漏掉的垃圾消息
2. **持续优化**：定期使用 `/feedspam` 投喂新的广告样本
3. **检查误判**：定期使用 `/listspam` 检查是否有误判
4. **数据备份**：定期备份 `data/` 目录

***

## 🐳 Docker部署

### 构建镜像

```bash
# 构建镜像
docker build -t spam-bot .

# 运行容器
docker run -d \
  --name spam-bot \
  -e BOT_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  spam-bot
```

### 使用 Docker Compose（推荐）

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down

# 重启
docker-compose restart

# 更新
docker-compose pull
docker-compose up -d
```

### 生产环境建议

1. **使用反向代理**：Nginx 或 Traefik
2. **SSL/TLS**：Let's Encrypt 自动证书
3. **自动重启**：配置 `restart: always` 或 `unless-stopped`
4. **日志收集**：使用 ELK 或 Loki
5. **监控告警**：配置健康检查失败告警
6. **资源限制**：

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

***

## ⚙️ 配置说明

在 `.env` 文件中可以调整以下配置：

```env
# Telegram Bot Token (必填)
BOT_TOKEN=your_bot_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/spam_bot.db

# 垃圾消息判定阈值 (0-1之间，默认0.95)
# 置信度超过此值才会判定为垃圾消息
# 值越高越严格，误判越少但漏检可能增加
SPAM_THRESHOLD=0.95

# 连续违规次数限制 (默认3次)
# 达到此次数将自动封禁用户
MAX_VIOLATIONS=3

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

***

## 🏗️ 项目结构

```
.
├── bayes_classifier.py    # 贝叶斯分类器核心
├── bot.py                 # Telegram Bot 主程序
├── config.py              # 配置管理
├── models.py              # 数据库模型
├── start.py               # 启动脚本
├── train_initial.py       # 初始训练脚本
├── test_classifier.py     # 分类器测试脚本
├── requirements.txt       # 依赖列表
├── .env.example           # 配置模板
├── Dockerfile             # Docker构建文件
├── docker-compose.yml     # Docker Compose配置
├── .dockerignore          # Docker忽略文件
├── README.md              # 项目说明
├── data/                  # 数据目录
│   ├── spam_bot.db       # SQLite数据库
│   └── bayes_model.pkl   # 训练好的模型
└── logs/                  # 日志目录
    └── bot.log
```

### 核心文件说明

- **bayes\_classifier.py**：朴素贝叶斯分类器，支持中文分词和拉普拉斯平滑
- **bot.py**：Telegram Bot主程序，包含所有命令处理和消息拦截逻辑
- **models.py**：SQLAlchemy数据库模型，管理训练数据、封禁用户等
- **train\_initial.py**：初始训练脚本，提供基础样本

***

## 🔧 核心算法

### 朴素贝叶斯分类

机器人使用朴素贝叶斯算法进行文本分类：

```
P(垃圾|文本) = P(文本|垃圾) * P(垃圾) / P(文本)
```

### 中文分词

使用 `jieba` 进行中文分词，针对中文广告特点优化：

- 支持中文词汇识别
- 过滤停用词和短词
- 保留关键词特征

### 拉普拉斯平滑

使用拉普拉斯平滑处理未出现过的词汇，避免零概率问题：

```
P(词|类别) = (词频 + α) / (总词数 + α * 词汇表大小)
```

### 对数概率计算

使用对数概率避免数值下溢：

```python
log_p = log(P(垃圾)) + Σ log(P(词|垃圾))
```

***

## 📊 模型优化

### 1. 初期训练

机器人刚部署时识别率可能不高，这是正常的。建议：

- 积极使用 `/markspam` 标记漏掉的垃圾消息
- 鼓励群成员使用 `/feedspam` 投喂训练数据
- 定期查看 `/listspam` 检查误判情况

### 2. 避免误判

如果正常消息被误判：

1. 使用 `/listspam` 查看被删除的消息
2. 如果发现误判，点击"标记为正常"按钮
3. 或者使用 `/feedspam` 投喂正常消息作为对比

### 3. 持续优化

- 定期投喂新的垃圾广告样本
- 收集不同行业的广告特征
- 关注误判案例，及时调整阈值

### 4. 阈值调整

根据实际情况调整 `SPAM_THRESHOLD`：

- **0.90-0.93**：更敏感，拦截更多但可能误判
- **0.95**（默认）：平衡，推荐
- **0.97-0.99**：更严格，误判少但可能漏检

***

## 🐛 常见问题

### Q: 为什么有些广告没有被识别？

**A:** 贝叶斯算法是概率算法，如果模型没有见过类似的广告，就无法准确识别。请使用 `/markspam` 或 `/feedspam` 投喂训练数据。

### Q: 正常消息被误删了怎么办？

**A:** 使用 `/listspam` 查看被删除的消息，如果发现误判，可以标记为正常。同时建议投喂一些正常消息作为对比训练。

### Q: 如何查看被删除的消息？

**A:** 使用 `/listspam` 命令可以查看最近被标记为垃圾的消息列表。

### Q: 可以自定义阈值吗？

**A:** 可以，修改 `.env` 文件中的 `SPAM_THRESHOLD` 值。值越高越严格（默认0.95）。

### Q: Docker部署后数据会丢失吗？

**A:** 不会。`data/` 和 `logs/` 目录已挂载到宿主机，容器重启数据不会丢失。

### Q: 如何备份数据？

**A:**

```bash
# 备份
tar -czvf backup-$(date +%Y%m%d).tar.gz data/ logs/

# 恢复
tar -xzvf backup-20240101.tar.gz
```

### Q: 支持多群组吗？

**A:** 支持！所有群组共享同一个训练模型，一处训练，全局受益。

### Q: 机器人需要哪些权限？

**A:**

- 删除消息（必需）
- 封禁用户（必需）
- 读取消息（必需）

### Q: 如何更新机器人？

**A:**

```bash
# 直接部署
git pull
pip install -r requirements.txt
python start.py

# Docker部署
git pull
docker-compose up -d --build
```

***

## 📝 更新日志

### v1.0.0 (2024-01-01)

- ✨ 初始版本发布
- 🛡️ 基于贝叶斯算法的垃圾消息识别
- 📚 支持投喂训练数据
- 👮 自动封禁违规用户
- 🤖 自动注册命令菜单
- 🐳 Docker部署支持

***

## 🤝 贡献

欢迎通过以下方式贡献：

1. **投喂训练数据** - 使用 `/feedspam` 命令
2. **反馈误判案例** - 帮助改进算法
3. **代码贡献** - 提交PR
4. **分享推广** - 让更多人使用

***

## ⚠️ 注意事项

1. **权限要求**：机器人需要删除消息和封禁用户的权限才能正常工作
2. **误判可能**：由于即时通讯消息"短文本+无上下文"的特性，完全避免误判很难
3. **隐私保护**：机器人只存储消息文本用于训练，不存储用户其他信息
4. **数据共享**：所有使用同一机器人的群组共享训练模型
5. **合规使用**：请遵守当地法律法规和Telegram使用条款

***

## 📄 许可证

MIT License

***

**感谢使用贝叶斯Telegram广告拦截机器人！** 🤖
