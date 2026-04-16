#!/usr/bin/env python3
"""
启动脚本
"""
import os
import sys
from pathlib import Path

# 确保目录存在
def ensure_directories():
    """创建必要的目录"""
    dirs = ['data', 'logs']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

if __name__ == "__main__":
    ensure_directories()
    
    # 检查 .env 文件
    if not Path('.env').exists():
        print("错误: 找不到 .env 配置文件")
        print("请复制 .env.example 为 .env 并配置你的 Bot Token")
        print("\n执行: cp .env.example .env")
        sys.exit(1)
    
    # 启动机器人
    from bot import main
    import asyncio
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n机器人已停止")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
