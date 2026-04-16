# 🤖 贝叶斯Telegram广告拦截机器人

一个基于朴素贝叶斯算法的轻量智能Telegram广告拦截机器人，具备自学习能力，可以通过投喂训练数据不断提升识别准确率。

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
- [部署指南](#-部署指南) - 三种部署方式
- [使用教程](#-使用教程) - 详细使用说明
- [配置说明](#-配置说明) - 参数配置
- [常见问题](#-常见问题) - 问题排查

---

## 🚀 快速开始


1. 在 [添加机器人](https://t.me/ad_qjtybot)

### 环境要求

- Python 3.8+
- pip
- 至少 512MB 内存

### 1. 获取 Bot Token

1. 在 Telegram 搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置名称和用户名
4. 复制获得的 Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 添加到群组

1. 在 Telegram 群组中搜索你的机器人
2. 添加到群组
3. **必须给予管理员权限**：
   - ✅ 删除消息
   - ✅ 封禁用户

机器人会自动开始工作！

---

## 🖥️ 部署指南

### 方式一：一键安装脚本（推荐）

适用于：Linux 服务器（Ubuntu/CentOS/Debian）

```bash
# 下载并运行安装脚本
wget https://raw.githubusercontent.com/luosxn/AD_bayes_telegramBOT/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

脚本会自动：
- 检测操作系统并安装依赖
- 交互式选择数据库类型（SQLite/PostgreSQL/MySQL）
- 配置 Telegram Bot Token
- 创建 systemd 服务
- 启动机器人

安装完成后：
```bash
# 查看状态
sudo systemctl status spam-bot

# 查看日志
sudo journalctl -u spam-bot -f

# 管理命令
sudo systemctl start|stop|restart spam-bot
```

---

### 方式二：Docker 部署

适用于：有 Docker 环境的用户

#### 使用 Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git
cd AD_bayes_telegramBOT

# 创建配置文件
cp .env.example .env
vim .env  # 编辑 BOT_TOKEN

# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

#### 使用 Docker 直接运行

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
```

---

### 方式三：Python 直接运行

适用于：本地测试或开发环境

```bash
# 克隆项目
git clone https://github.com/luosxn/AD_bayes_telegramBOT.git
cd AD_bayes_telegramBOT

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置
cp .env.example .env
nano .env  # 编辑 BOT_TOKEN

# 运行
python start.py
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

---

## ⚙️ 配置说明

### 基础配置

编辑 `.env` 文件：

```env
# 必填：Bot Token
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# 可选：垃圾判定阈值（0-1，默认0.95）
SPAM_THRESHOLD=0.95

# 可选：违规次数限制（默认3次）
MAX_VIOLATIONS=3

# 可选：日志级别
LOG_LEVEL=INFO
```

### 数据库配置

支持 **SQLite**、**PostgreSQL**、**MySQL** 三种数据库：

#### SQLite（默认，适合单机部署）

```env
DATABASE_URL=sqlite:///./data/spam_bot.db
```

✅ 无需额外安装，开箱即用  
⚠️ 不适合高并发或多机部署

#### PostgreSQL（推荐用于生产环境）

```env
DATABASE_URL=postgresql://username:password@localhost:5432/spam_bot
```

安装驱动：
```bash
pip install psycopg2-binary
```

#### MySQL

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/spam_bot
```

安装驱动：
```bash
pip install pymysql
```

### 数据库选择建议

| 场景 | 推荐数据库 | 理由 |
|-----|-----------|------|
| 个人使用/测试 | SQLite | 简单，无需配置 |
| 生产环境/多群组 | PostgreSQL | 稳定，性能好 |
| 已有 MySQL 环境 | MySQL | 统一管理 |

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

### Q: Docker 部署后如何更新？

```bash
cd AD_bayes_telegramBOT

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

---

## 📁 项目结构

```
AD_bayes_telegramBOT/
├── bayes_classifier.py    # 贝叶斯分类器核心
├── bot.py                 # Telegram Bot 主程序
├── config.py              # 配置管理
├── models.py              # 数据库模型
├── start.py               # 启动脚本
├── train_initial.py       # 初始训练脚本
├── install.sh             # 一键安装脚本
├── Dockerfile             # Docker 镜像构建
├── docker-compose.yml     # Docker Compose 配置
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
