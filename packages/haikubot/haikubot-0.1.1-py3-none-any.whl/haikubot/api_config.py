"""
API配置模块
"""
import os
import json
from pathlib import Path

# 配置文件存储位置
CONFIG_DIR = Path.home() / ".config" / "haikubot"
CONFIG_FILE = CONFIG_DIR / "config.json"

def save_api_key(api_key):
    """保存API密钥到配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)
    # 设置权限为只有用户可读写
    os.chmod(CONFIG_FILE, 0o600)
    return True

def get_api_key():
    """从配置文件或环境变量获取API密钥"""
    # 首先尝试从环境变量获取
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if api_key:
        return api_key
    
    # 然后尝试从配置文件获取
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("api_key")
        except (json.JSONDecodeError, IOError):
            pass
    
    return None 