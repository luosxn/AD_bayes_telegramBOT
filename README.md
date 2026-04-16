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

## 📋 目录

- [快速开始](#-快速开始) - 5分钟快速运行
- [部署指南](#-部署指南) - 多种部署方式
- [使用教程](#-使用教程) - 详细使用说明
- [配置说明](#-配置说明) - 参数配置
- [常见问题](#-常见问题) - 问题排查

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip
- 至少 512MB 内存

### 1. 获取 Bot Token

1. 在 Telegram 搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置名称和用户名
4. 复制获得的 Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 安装并运行

#### 方式一：一键安装脚本（推荐）

```bash
# 下载并运行安装脚本
wget https://raw.githubusercontent.com/luosxn/AD_bayes_telegramBOT/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

脚本会自动：
- 检测操作系统并安装依赖
- 交互式选择数据库类型
- 配置 Telegram Bot Token
- 创建 systemd 服务
- 启动机器人

#### 方式二：手动安装

```bash
# 克隆项目
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git
cd AD_bayes_telegramBOT

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置
cp .env.example .env
# 编辑 .env 文件，将 your_bot_token_here 替换为你的 Token

# 运行
python start.py
```

### 3. 添加到群组

1. 在 Telegram 群组中搜索你的机器人
2. 添加到群组
3. **必须给予管理员权限**：
   - ✅ 删除消息
   - ✅ 封禁用户

机器人会自动开始工作！

---

## 🖥️ 部署指南

### 部署方式对比

| 方式 | 适用场景 | 稳定性 | 难度 |
|-----|---------|-------|------|
| [systemd](#systemd-推荐) | Linux服务器生产环境 | ⭐⭐⭐ | ⭐⭐ |
| [Docker](#docker) | 容器化部署 | ⭐⭐⭐ | ⭐⭐ |
| [PM2](#pm2) | Node.js用户 | ⭐⭐⭐ | ⭐⭐ |
| [Heroku](#heroku) | 免费托管 | ⭐⭐ | ⭐ |
| [Railway](#railway) | 免费托管 | ⭐⭐ | ⭐ |
| [VPS](#vps推荐) | 自建服务器 | ⭐⭐⭐ | ⭐⭐ |

---

### systemd（推荐）

适用于：Ubuntu/CentOS/Debian 等 Linux 服务器

#### 步骤 1：准备环境

```bash
# 连接服务器
ssh user@your-server-ip

# 安装依赖
sudo apt update
sudo apt install -y python3 python3-venv git

# 克隆项目
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git /opt/spam-bot
cd /opt/spam-bot

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置
cp .env.example .env
nano .env  # 编辑 BOT_TOKEN
```

#### 步骤 2：创建服务文件

```bash
sudo nano /etc/systemd/system/spam-bot.service
```

粘贴以下内容：

```ini
[Unit]
Description=Telegram Spam Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/spam-bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/spam-bot/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 步骤 3：启动服务

```bash
# 重载配置
sudo systemctl daemon-reload

# 设置开机自启
sudo systemctl enable spam-bot

# 启动服务
sudo systemctl start spam-bot

# 查看状态
sudo systemctl status spam-bot
```

#### 常用命令

```bash
# 查看日志
sudo journalctl -u spam-bot -f

# 重启
sudo systemctl restart spam-bot

# 停止
sudo systemctl stop spam-bot

# 查看最近100行日志
sudo journalctl -u spam-bot -n 100
```

---

### Docker

#### 使用 Docker 运行

```bash
# 克隆项目
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git

cd AD_bayes_telegramBOT

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 设置 BOT_TOKEN

# 运行容器
docker run -d \
  --name spam-bot \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env:ro \
  python:3.11-slim \
  bash -c "pip install -r requirements.txt && python start.py"
```

#### 使用 docker-compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  spam-bot:
    image: python:3.11-slim
    container_name: spam-bot
    restart: unless-stopped
    working_dir: /app
    volumes:
      - ./:/app
      - ./data:/app/data
      - ./logs:/app/logs
    command: >
      bash -c "pip install -r requirements.txt &&
               python start.py"
```

运行：

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down

# 重启
docker-compose restart
```

---

### PM2

适用于：熟悉 Node.js 生态的用户

```bash
# 安装 PM2
npm install -g pm2

# 创建配置文件
nano ecosystem.config.js
```

配置文件内容：

```javascript
module.exports = {
  apps: [{
    name: 'spam-bot',
    script: 'start.py',
    interpreter: './venv/bin/python',
    cwd: '/path/to/spam-bot',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      PYTHONUNBUFFERED: '1'
    },
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
```

启动：

```bash
# 启动
pm2 start ecosystem.config.js

# 保存配置
pm2 save
pm2 startup

# 查看状态
pm2 status
pm2 logs spam-bot

# 管理
pm2 restart spam-bot
pm2 stop spam-bot
```

---

### Heroku

适用于：快速免费部署

```bash
# 安装 Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 登录
heroku login

# 创建应用
heroku create your-bot-name

# 设置环境变量
heroku config:set BOT_TOKEN=your_bot_token_here

# 部署
git push heroku main

# 查看日志
heroku logs --tail

# 确保至少运行一个实例
heroku ps:scale worker=1
```

> ⚠️ **注意**：Heroku 免费 dyno 会休眠，需要配合监控保持活跃

---

### Railway

适用于：免费且更稳定的托管

1. Fork 本项目到你的 GitHub 账号
2. 访问 [Railway](https://railway.app) 并登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的仓库
5. 点击 "Add Variables"，添加 `BOT_TOKEN`
6. 部署完成！

> ✅ **优点**：免费额度充足，不会休眠，有持久化存储

---

### VPS（推荐）

适用于：阿里云、腾讯云、AWS、DigitalOcean 等

#### 推荐配置

- **最低配置**：1核 CPU / 512MB 内存 / 10GB 存储
- **推荐配置**：1核 CPU / 1GB 内存 / 20GB 存储
- **系统**：Ubuntu 20.04/22.04 LTS

#### 一键部署脚本

```bash
#!/bin/bash
# deploy.sh - 一键部署脚本

set -e

echo "🚀 开始部署 Telegram Spam Bot..."

# 安装依赖
echo "📦 安装依赖..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git

# 创建目录
sudo mkdir -p /opt/spam-bot
sudo chown $USER:$USER /opt/spam-bot

# 克隆代码
echo "📥 下载代码..."
cd /opt/spam-bot
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git .

# 创建虚拟环境
echo "🐍 创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置
echo "⚙️ 配置..."
cp .env.example .env
echo "请编辑 .env 文件设置 BOT_TOKEN"
nano .env

# 创建 systemd 服务
echo "🔧 创建服务..."
sudo tee /etc/systemd/system/spam-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram Spam Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/spam-bot
ExecStart=/opt/spam-bot/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable spam-bot
sudo systemctl start spam-bot

echo "✅ 部署完成！"
echo "查看日志: sudo journalctl -u spam-bot -f"
```

使用方法：

```bash
# 下载并运行
wget https://raw.githubusercontent.com/yourusername/spam-bot/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

---

## 📖 使用教程

### 命令列表

输入 `/` 可查看所有命令，支持自动补全。

#### 管理员命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/markspam` | 标记垃圾消息并封禁用户 | 回复垃圾消息 + `/markspam` |
| `/listbanuser` | 查看封禁用户列表 | `/listbanuser` |
| `/listspam` | 查看垃圾消息记录 | `/listspam` |
| `/unban` | 解封用户 | `/unban` 或回复用户消息 + `/unban` |

#### 普通命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/feedspam` | 投喂垃圾消息训练 | `/feedspam 文本内容` |
| `/stats` | 查看统计信息 | `/stats` |
| `/help` | 查看帮助 | `/help` |
| `/start` | 开始使用 | `/start` |

### 训练机器人

#### 方法 1：回复标记（推荐）

当机器人漏掉垃圾消息时：
1. 回复那条垃圾消息
2. 发送 `/markspam`
3. 机器人会删除消息、封禁用户，并学习这条消息

#### 方法 2：投喂训练

```
/feedspam 这里是要训练的垃圾广告内容，比如：出售微信号，联系 @seller
```

#### 方法 3：私聊投喂

直接私聊机器人发送 `/feedspam`，不会影响任何群组。

### 查看被删除的消息

```
/listspam
```

可以查看最近被标记的垃圾消息，如果发现误判，可以点击按钮标记为正常。

---

## ⚙️ 配置说明

编辑 `.env` 文件：

```env
# 必填：Bot Token
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# 可选：数据库路径
DATABASE_URL=sqlite:///./data/spam_bot.db

# 可选：垃圾判定阈值（0-1，默认0.95）
# 越高越严格，越低越宽松
SPAM_THRESHOLD=0.95

# 可选：违规次数限制（默认3次）
MAX_VIOLATIONS=3

# 可选：日志级别
LOG_LEVEL=INFO
```

---

## 🔧 数据备份

### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar czf $BACKUP_DIR/spam_bot_$DATE.tar.gz data/ .env

# 保留30天
find $BACKUP_DIR -name "spam_bot_*.tar.gz" -mtime +30 -delete

echo "✅ 备份完成: $BACKUP_DIR/spam_bot_$DATE.tar.gz"
```

添加定时任务：

```bash
crontab -e
# 每天凌晨3点备份
0 3 * * * /path/to/backup.sh >> /path/to/backup.log 2>&1
```

### 迁移服务器

只需复制以下文件到新服务器：
- `.env` 配置文件
- `data/` 目录（数据库和模型）

然后重新安装依赖即可。

---

## 🐛 常见问题

### Q: 机器人不工作？

检查清单：
1. ✅ 查看日志：`logs/bot.log` 或 `journalctl -u spam-bot -f`
2. ✅ 确认 Token 正确
3. ✅ 确认网络连接
4. ✅ 确认给了管理员权限（删除消息 + 封禁用户）

### Q: 为什么有些广告没识别？

贝叶斯算法需要学习。请使用 `/markspam` 或 `/feedspam` 投喂训练数据，机器人会越用越准。

### Q: 正常消息被误删？

使用 `/listspam` 查看被删除的消息，如果发现误判，可以标记为正常。

### Q: 如何调整敏感度？

编辑 `.env`：
- `SPAM_THRESHOLD=0.90` - 更敏感（可能误判更多）
- `SPAM_THRESHOLD=0.98` - 更严格（可能漏掉更多）

### Q: 免费部署推荐？

推荐优先级：
1. **Railway** - 免费、稳定、有持久化
2. **Heroku** - 免费但会休眠
3. **Oracle Cloud** - 永久免费 VPS

---

## 📁 项目结构

```
spam-bot/
├── bayes_classifier.py    # 贝叶斯分类器核心
├── bot.py                 # Telegram Bot 主程序
├── config.py              # 配置管理
├── models.py              # 数据库模型
├── start.py               # 启动脚本
├── train_initial.py       # 初始训练脚本
├── requirements.txt       # 依赖列表
├── .env.example           # 配置模板
├── data/                  # 数据目录（自动创建）
│   ├── spam_bot.db       # SQLite数据库
│   └── bayes_model.pkl   # 训练好的模型
└── logs/                  # 日志目录（自动创建）
    └── bot.log
```

---

## 🤝 贡献

- 投喂训练数据：使用 `/feedspam`
- 反馈问题：提交 Issue
- 代码贡献：提交 PR

## 📄 许可证

MIT License

## 🙏 致谢

- 灵感来源于 [bayes_spam_sniper](https://github.com/ramsayleung/bayes_spam_sniper)
- 保罗·格雷厄姆的贝叶斯垃圾邮件过滤思想
