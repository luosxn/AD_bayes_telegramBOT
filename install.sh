#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="AD_bayes_telegramBOT"
GITHUB_REPO="https://github.com/luosxn/AD_bayes_telegramBOT.git"
INSTALL_DIR="/opt/spam-bot"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [[ -f /etc/lsb-release ]]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
}

# 安装系统依赖
install_system_deps() {
    print_step "步骤 1/5: 安装系统依赖"
    
    print_info "检测到操作系统: $OS $VER"
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        print_info "正在更新软件包列表..."
        apt-get update -qq
        
        print_info "正在安装依赖..."
        apt-get install -y -qq python3 python3-venv python3-pip git curl wget
        
        # 根据数据库选择安装额外依赖
        if [[ "$DB_TYPE" == "postgresql" ]]; then
            print_info "正在安装 PostgreSQL 客户端..."
            apt-get install -y -qq postgresql-client libpq-dev
        elif [[ "$DB_TYPE" == "mysql" ]]; then
            print_info "正在安装 MySQL 客户端..."
            apt-get install -y -qq default-libmysqlclient-dev
        fi
        
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
        print_info "正在安装依赖..."
        yum install -y -q python3 python3-venv python3-pip git curl wget
        
        if [[ "$DB_TYPE" == "postgresql" ]]; then
            print_info "正在安装 PostgreSQL 客户端..."
            yum install -y -q postgresql
        elif [[ "$DB_TYPE" == "mysql" ]]; then
            print_info "正在安装 MySQL 客户端..."
            yum install -y -q mysql
        fi
        
    elif [[ "$OS" == *"Alpine"* ]]; then
        print_info "正在安装依赖..."
        apk add --no-cache python3 py3-virtualenv py3-pip git curl wget
        
        if [[ "$DB_TYPE" == "postgresql" ]]; then
            apk add --no-cache postgresql-client postgresql-dev
        elif [[ "$DB_TYPE" == "mysql" ]]; then
            apk add --no-cache mysql-client mariadb-dev
        fi
        
    else
        print_warning "未知的操作系统，尝试使用通用安装方法..."
        if command_exists apt-get; then
            apt-get update -qq && apt-get install -y -qq python3 python3-venv python3-pip git
        elif command_exists yum; then
            yum install -y -q python3 python3-venv python3-pip git
        elif command_exists pacman; then
            pacman -Sy --noconfirm python python-virtualenv python-pip git
        else
            print_error "无法自动安装依赖，请手动安装 Python 3.8+ 和 pip"
            exit 1
        fi
    fi
    
    print_success "系统依赖安装完成"
}

# 选择数据库类型
select_database() {
    print_step "步骤 2/5: 选择数据库类型"
    
    echo "请选择数据库类型:"
    echo ""
    echo "  1) SQLite (默认，适合单机部署，无需配置)"
    echo "  2) PostgreSQL (推荐用于生产环境，高性能)"
    echo "  3) MySQL (广泛使用，易于维护)"
    echo ""
    
    while true; do
        read -p "请输入选项 [1-3] (默认: 1): " db_choice
        db_choice=${db_choice:-1}
        
        case $db_choice in
            1)
                DB_TYPE="sqlite"
                DB_URL="sqlite:///./data/spam_bot.db"
                print_success "选择的数据库: SQLite"
                break
                ;;
            2)
                DB_TYPE="postgresql"
                configure_postgresql
                break
                ;;
            3)
                DB_TYPE="mysql"
                configure_mysql
                break
                ;;
            *)
                print_error "无效选项，请重新输入"
                ;;
        esac
    done
}

# 配置 PostgreSQL
configure_postgresql() {
    print_info "配置 PostgreSQL 连接信息"
    echo ""
    
    read -p "数据库主机 [localhost]: " db_host
    db_host=${db_host:-localhost}
    
    read -p "数据库端口 [5432]: " db_port
    db_port=${db_port:-5432}
    
    read -p "数据库名称 [spam_bot]: " db_name
    db_name=${db_name:-spam_bot}
    
    read -p "数据库用户名: " db_user
    while [[ -z "$db_user" ]]; do
        print_error "用户名不能为空"
        read -p "数据库用户名: " db_user
    done
    
    read -s -p "数据库密码: " db_pass
    echo ""
    while [[ -z "$db_pass" ]]; do
        print_error "密码不能为空"
        read -s -p "数据库密码: " db_pass
        echo ""
    done
    
    DB_URL="postgresql://${db_user}:${db_pass}@${db_host}:${db_port}/${db_name}"
    print_success "PostgreSQL 配置完成"
}

# 配置 MySQL
configure_mysql() {
    print_info "配置 MySQL 连接信息"
    echo ""
    
    read -p "数据库主机 [localhost]: " db_host
    db_host=${db_host:-localhost}
    
    read -p "数据库端口 [3306]: " db_port
    db_port=${db_port:-3306}
    
    read -p "数据库名称 [spam_bot]: " db_name
    db_name=${db_name:-spam_bot}
    
    read -p "数据库用户名: " db_user
    while [[ -z "$db_user" ]]; do
        print_error "用户名不能为空"
        read -p "数据库用户名: " db_user
    done
    
    read -s -p "数据库密码: " db_pass
    echo ""
    while [[ -z "$db_pass" ]]; do
        print_error "密码不能为空"
        read -s -p "数据库密码: " db_pass
        echo ""
    done
    
    DB_URL="mysql+pymysql://${db_user}:${db_pass}@${db_host}:${db_port}/${db_name}"
    print_success "MySQL 配置完成"
}

# 配置 Telegram Bot
configure_telegram() {
    print_step "步骤 3/5: 配置 Telegram Bot"
    
    echo ""
    echo "请从 @BotFather 获取 Bot Token"
    echo "步骤:"
    echo "  1. 在 Telegram 搜索 @BotFather"
    echo "  2. 发送 /newbot 创建新机器人"
    echo "  3. 按提示设置名称和用户名"
    echo "  4. 复制获得的 Token"
    echo ""
    
    while true; do
        read -p "请输入 Bot Token: " bot_token
        
        if [[ -z "$bot_token" ]]; then
            print_error "Bot Token 不能为空"
            continue
        fi
        
        # 简单验证 Token 格式
        if [[ ! "$bot_token" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
            print_warning "Token 格式似乎不正确，但将继续使用"
        fi
        
        BOT_TOKEN=$bot_token
        break
    done
    
    print_success "Bot Token 已配置"
    
    # 可选配置
    echo ""
    print_info "可选配置 (直接回车使用默认值)"
    
    read -p "垃圾消息判定阈值 [0.95]: " threshold
    THRESHOLD=${threshold:-0.95}
    
    read -p "最大违规次数 [3]: " max_violations
    MAX_VIOLATIONS=${max_violations:-3}
    
    read -p "日志级别 [INFO]: " log_level
    LOG_LEVEL=${log_level:-INFO}
}

# 下载并安装项目
install_project() {
    print_step "步骤 4/5: 下载并安装项目"
    
    # 创建安装目录
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "安装目录已存在: $INSTALL_DIR"
        read -p "是否删除并重新安装? [y/N]: " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_info "使用现有目录"
        fi
    fi
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR" || exit 1
    
    # 克隆代码
    print_info "正在下载项目..."
    if ! git clone "$GITHUB_REPO" .; then
        print_error "下载失败，请检查网络连接"
        exit 1
    fi
    
    print_success "项目下载完成"
    
    # 创建虚拟环境
    print_info "正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装依赖
    print_info "正在安装 Python 依赖..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    print_success "依赖安装完成"
}

# 创建配置文件
create_config() {
    print_step "步骤 5/5: 创建配置文件"
    
    # 创建 .env 文件
    cat > "$INSTALL_DIR/.env" << EOF
# Telegram Bot Token
BOT_TOKEN=$BOT_TOKEN

# 数据库配置
DATABASE_URL=$DB_URL

# 垃圾消息判定阈值
SPAM_THRESHOLD=$THRESHOLD

# 连续违规次数限制
MAX_VIOLATIONS=$MAX_VIOLATIONS

# 日志级别
LOG_LEVEL=$LOG_LEVEL
EOF
    
    print_success "配置文件已创建: $INSTALL_DIR/.env"
    
    # 创建数据目录
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/logs"
    
    # 创建 systemd 服务文件
    create_systemd_service
}

# 创建 systemd 服务
create_systemd_service() {
    print_info "创建 systemd 服务..."
    
    # 获取当前用户
    CURRENT_USER=$(whoami)
    
    # 创建服务文件
    sudo tee /etc/systemd/system/spam-bot.service > /dev/null << EOF
[Unit]
Description=Telegram Spam Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$INSTALL_DIR/venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 重载 systemd
    sudo systemctl daemon-reload
    sudo systemctl enable spam-bot
    
    print_success "systemd 服务已创建"
}

# 测试数据库连接
test_db_connection() {
    if [[ "$DB_TYPE" == "sqlite" ]]; then
        return 0
    fi
    
    print_info "测试数据库连接..."
    
    source "$INSTALL_DIR/venv/bin/activate"
    
    python3 << EOF
import sys
sys.path.insert(0, '$INSTALL_DIR')

from config import get_settings
from models import init_db

try:
    init_db()
    print("${GREEN}[SUCCESS]${NC} 数据库连接成功")
    sys.exit(0)
except Exception as e:
    print(f"${RED}[ERROR]${NC} 数据库连接失败: {e}")
    sys.exit(1)
EOF
    
    if [[ $? -ne 0 ]]; then
        print_error "数据库连接测试失败，请检查配置"
        return 1
    fi
    
    return 0
}

# 启动服务
start_service() {
    print_step "启动服务"
    
    read -p "是否立即启动机器人? [Y/n]: " start_now
    start_now=${start_now:-Y}
    
    if [[ "$start_now" =~ ^[Yy]$ ]]; then
        sudo systemctl start spam-bot
        sleep 2
        
        if sudo systemctl is-active --quiet spam-bot; then
            print_success "机器人启动成功!"
            echo ""
            echo -e "查看日志: ${CYAN}sudo journalctl -u spam-bot -f${NC}"
            echo -e "查看状态: ${CYAN}sudo systemctl status spam-bot${NC}"
        else
            print_error "机器人启动失败"
            echo -e "查看错误: ${CYAN}sudo journalctl -u spam-bot -n 50${NC}"
        fi
    else
        print_info "跳过启动"
        echo -e "手动启动: ${CYAN}sudo systemctl start spam-bot${NC}"
    fi
}

# 显示安装摘要
show_summary() {
    print_step "安装摘要"
    
    echo ""
    echo -e "${GREEN}✓${NC} 项目安装路径: ${CYAN}$INSTALL_DIR${NC}"
    echo -e "${GREEN}✓${NC} 数据库类型: ${CYAN}$DB_TYPE${NC}"
    echo -e "${GREEN}✓${NC} 配置文件: ${CYAN}$INSTALL_DIR/.env${NC}"
    echo -e "${GREEN}✓${NC} 服务名称: ${CYAN}spam-bot${NC}"
    echo ""
    echo "常用命令:"
    echo -e "  启动: ${CYAN}sudo systemctl start spam-bot${NC}"
    echo -e "  停止: ${CYAN}sudo systemctl stop spam-bot${NC}"
    echo -e "  重启: ${CYAN}sudo systemctl restart spam-bot${NC}"
    echo -e "  状态: ${CYAN}sudo systemctl status spam-bot${NC}"
    echo -e "  日志: ${CYAN}sudo journalctl -u spam-bot -f${NC}"
    echo ""
    
    if [[ "$DB_TYPE" == "sqlite" ]]; then
        echo -e "${YELLOW}注意:${NC} SQLite 数据库文件位于: $INSTALL_DIR/data/spam_bot.db"
    fi
    
    echo ""
    echo -e "${GREEN}安装完成!${NC}"
}

# 主函数
main() {
    # 检查 root 权限
    if [[ $EUID -eq 0 ]]; then
        print_warning "不建议使用 root 用户运行此脚本"
        read -p "是否继续? [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 检查 sudo 权限
    if ! sudo -n true 2>/dev/null; then
        print_info "需要 sudo 权限来安装系统依赖和创建服务"
        sudo -v
    fi
    
    # 清屏
    clear
    
    # 打印欢迎信息
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║     🤖 贝叶斯 Telegram 广告拦截机器人 - 交互式安装脚本      ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    # 检测系统
    detect_os
    print_info "检测到操作系统: $OS $VER"
    echo ""
    
    # 执行安装步骤
    select_database
    configure_telegram
    install_system_deps
    install_project
    create_config
    
    # 测试数据库连接
    if ! test_db_connection; then
        print_warning "数据库连接测试失败，但安装已完成"
        print_info "请检查数据库配置后手动启动服务"
    fi
    
    # 启动服务
    start_service
    
    # 显示摘要
    show_summary
}

# 捕获中断信号
trap 'print_error "安装被中断"; exit 1' INT TERM

# 运行主函数
main
