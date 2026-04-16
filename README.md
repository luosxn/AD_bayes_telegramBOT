# 🤖 贝叶斯Telegram广告拦截机器人

一个基于朴素贝叶斯算法的智能Telegram广告拦截机器人，具备自学习能力，可以通过投喂训练数据不断提升识别准确率。

## ✨ 特性

- 🛡️ **智能拦截** - 基于贝叶斯算法自动识别垃圾广告，置信度超过95%才会拦截
- 📚 **自主学习** - 支持投喂训练数据，模型实时更新
- 👮 **自动封禁** - 连续违规3次自动封禁用户
- 🔄 **实时更新** - 所有群组共享同一个训练模型，一处训练，全局受益
- 💾 **数据持久化** - 训练数据和模型自动保存，重启不丢失
- 🎯 **中文优化** - 使用jieba进行中文分词，针对中文广告优化
- 🤖 **自动命令** - 启动时自动注册命令菜单，支持命令自动补全

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip
- 至少 512MB 内存
- 稳定的网络连接

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

复制配置文件模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Bot Token：

```env
BOT_TOKEN=your_bot_token_here
```

> 获取 Bot Token：在 Telegram 中搜索 [@BotFather](https://t.me/BotFather)，创建新机器人获取 Token。

### 4. 初始训练（可选）

运行初始训练脚本，提供一些基础样本：

```bash
python train_initial.py
```

### 5. 启动机器人

```bash
python start.py
```

## 📖 使用方法

### 添加到群组

1. 将机器人添加到群组
2. 给予管理员权限：
   - ✅ 删除消息
   - ✅ 封禁用户
3. 机器人自动开始工作

### 可用命令

#### 管理员命令

| 命令 | 说明 | 用法 |
|------|------|------|
| `/markspam` | 标记垃圾消息并封禁用户 | 回复垃圾消息 + `/markspam` |
| `/listbanuser` | 查看封禁用户列表 | `/listbanuser` |
| `/listspam` | 查看被标记的垃圾消息 | `/listspam` |
| `/unban` | 解封用户 | `/unban` 或 `/unban 用户ID` |

#### 普通命令

| 命令 | 说明 | 用法 |
|------|------|------|
| `/feedspam` | 投喂垃圾消息训练 | `/feedspam 文本内容` 或回复消息 |
| `/stats` | 查看统计信息 | `/stats` |
| `/help` | 查看帮助 | `/help` |
| `/start` | 开始/欢迎信息 | `/start` |

### 投喂训练数据

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

## 🖥️ 部署教程

### 本地部署

#### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置
cp .env.example .env
# 编辑 .env 文件设置 BOT_TOKEN

# 运行
python start.py
```

#### 后台运行（Linux/Mac）

```bash
# 使用 nohup
nohup python start.py > bot.log 2>&1 &

# 或使用 screen
screen -S spam-bot
python start.py
# Ctrl+A, D 分离会话

# 重新连接
screen -r spam-bot
```

### 服务器部署

#### 使用 systemd（推荐用于 Linux 服务器）

1. 创建服务文件：

```bash
sudo nano /etc/systemd/system/spam-bot.service
```

2. 添加以下内容：

```ini
[Unit]
Description=Telegram Spam Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/your/bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/path/to/your/bot/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable spam-bot
sudo systemctl start spam-bot

# 查看状态
sudo systemctl status spam-bot

# 查看日志
sudo journalctl -u spam-bot -f
```

#### 使用 PM2（Node.js 进程管理器，也支持 Python）

```bash
# 安装 PM2
npm install -g pm2

# 创建 ecosystem 文件
pm2 ecosystem

# 编辑 ecosystem.config.js
module.exports = {
  apps: [{
    name: 'spam-bot',
    script: 'start.py',
    interpreter: 'python3',
    cwd: '/path/to/your/bot',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};

# 启动
pm2 start ecosystem.config.js

# 保存配置
pm2 save
pm2 startup

# 管理
pm2 status
pm2 logs spam-bot
pm2 restart spam-bot
pm2 stop spam-bot
```

#### 使用 Docker

1. 创建 Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p data logs

# 运行
CMD ["python", "start.py"]
```

2. 构建并运行：

```bash
# 构建镜像
docker build -t spam-bot .

# 运行容器
docker run -d \
  --name spam-bot \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  spam-bot

# 查看日志
docker logs -f spam-bot

# 停止
docker stop spam-bot
docker rm spam-bot
```

3. 使用 docker-compose：

```yaml
version: '3.8'

services:
  spam-bot:
    build: .
    container_name: spam-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    environment:
      - PYTHONUNBUFFERED=1
```

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 云平台部署

#### 部署到 Heroku

1. 创建必要的文件：

```bash
# Procfile
echo "worker: python start.py" > Procfile

# runtime.txt
echo "python-3.11.6" > runtime.txt
```

2. 部署：

```bash
# 登录 Heroku
heroku login

# 创建应用
heroku create your-bot-name

# 设置环境变量
heroku config:set BOT_TOKEN=your_bot_token

# 部署
git push heroku main

# 查看日志
heroku logs --tail
```

#### 部署到 Railway

1. Fork 本项目到你的 GitHub
2. 在 Railway 创建新项目，选择 GitHub 仓库
3. 添加环境变量 `BOT_TOKEN`
4. 部署完成

#### 部署到 VPS（如阿里云、腾讯云、AWS等）

```bash
# 1. 连接服务器
ssh user@your-server-ip

# 2. 安装 Python 和 git
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 3. 克隆代码
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# 4. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt

# 6. 配置
cp .env.example .env
nano .env  # 编辑配置

# 7. 使用 systemd 管理服务（见上文）
```

### 数据备份

#### 备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库和模型
tar czf $BACKUP_DIR/spam_bot_backup_$DATE.tar.gz data/

# 保留最近 30 天的备份
find $BACKUP_DIR -name "spam_bot_backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/spam_bot_backup_$DATE.tar.gz"
```

```bash
# 添加定时任务（每天凌晨3点备份）
crontab -e
0 3 * * * /path/to/your/bot/backup.sh >> /path/to/your/bot/logs/backup.log 2>&1
```

## ⚙️ 配置说明

在 `.env` 文件中可以调整以下配置：

```env
# Telegram Bot Token (必填)
BOT_TOKEN=your_bot_token_here

# 数据库配置
DATABASE_URL=sqlite:///./data/spam_bot.db

# 垃圾消息判定阈值 (0-1之间，默认0.95)
# 置信度超过此值才会判定为垃圾消息
SPAM_THRESHOLD=0.95

# 连续违规次数限制 (默认3次)
MAX_VIOLATIONS=3

# 日志级别
LOG_LEVEL=INFO
```

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
├── data/                  # 数据目录
│   ├── spam_bot.db       # SQLite数据库
│   └── bayes_model.pkl   # 训练好的模型
└── logs/                  # 日志目录
    └── bot.log
```

## 🔧 核心算法

### 朴素贝叶斯分类

机器人使用朴素贝叶斯算法进行文本分类：

```
P(垃圾|文本) = P(文本|垃圾) * P(垃圾) / P(文本)
```

### 中文分词

使用 `jieba` 进行中文分词，针对中文广告特点优化。

### 拉普拉斯平滑

使用拉普拉斯平滑处理未出现过的词汇，避免零概率问题。

## 📊 模型优化建议

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
- 关注误判案例，及时调整

## ⚠️ 注意事项

1. **权限要求**：机器人需要删除消息和封禁用户的权限才能正常工作
2. **误判可能**：由于即时通讯消息"短文本+无上下文"的特性，完全避免误判很难
3. **隐私保护**：机器人只存储消息文本用于训练，不存储用户其他信息
4. **数据共享**：所有使用同一机器人的群组共享训练模型
5. **网络要求**：需要稳定的网络连接，建议使用服务器部署

## 🐛 常见问题

### Q: 为什么有些广告没有被识别？

A: 贝叶斯算法是概率算法，如果模型没有见过类似的广告，就无法准确识别。请使用 `/markspam` 或 `/feedspam` 投喂训练数据。

### Q: 正常消息被误删了怎么办？

A: 使用 `/listspam` 查看被删除的消息，如果发现误判，可以标记为正常。同时建议投喂一些正常消息作为对比训练。

### Q: 如何查看被删除的消息？

A: 使用 `/listspam` 命令可以查看最近被标记为垃圾的消息列表。

### Q: 可以自定义阈值吗？

A: 可以，修改 `.env` 文件中的 `SPAM_THRESHOLD` 值。值越高越严格（默认0.95）。

### Q: 机器人停止工作了怎么办？

A: 检查以下几点：
1. 查看日志 `logs/bot.log` 或 `docker logs`
2. 确认网络连接正常
3. 确认 Bot Token 有效
4. 如果使用 systemd，检查 `systemctl status spam-bot`

### Q: 如何迁移到另一台服务器？

A: 只需复制以下文件：
- `.env` 配置文件
- `data/` 目录（包含数据库和模型）

然后在新服务器上重新安装依赖并启动即可。

## 🤝 贡献

欢迎通过以下方式贡献：

1. **投喂训练数据** - 使用 `/feedspam` 命令
2. **反馈误判案例** - 帮助改进算法
3. **代码贡献** - 提交PR

## 📄 许可证

MIT License

## 🙏 致谢

- 灵感来源于 [bayes_spam_sniper](https://github.com/ramsayleung/bayes_spam_sniper)
- 保罗·格雷厄姆的贝叶斯垃圾邮件过滤思想
