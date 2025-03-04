#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from .core import process_video
from .api_config import get_api_key, save_api_key

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='从Bilibili视频生成俳句的命令行工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 处理视频命令
    process_parser = subparsers.add_parser('--process', help='处理视频并生成俳句')
    process_parser.add_argument('bvid', help='Bilibili视频的BV号')
    
    # 配置API密钥命令
    config_parser = subparsers.add_parser('--config', help='配置API密钥')
    config_parser.add_argument('key', help='设置DashScope API密钥')
    
    # 版本信息命令
    version_parser = subparsers.add_parser('--version', help='显示版本信息')
    
    args = parser.parse_args()
    
    # 如果没有指定子命令，尝试将第一个参数作为BV号处理
    if not args.command:
        if len(sys.argv) > 1 and sys.argv[1].startswith('BV'):
            bvid = sys.argv[1]
            return process_command(bvid)
        else:
            parser.print_help()
            return
    
    # 根据子命令执行不同的操作
    if args.command == '--process':
        return process_command(args.bvid)
    elif args.command == '--config':
        return config_command(args.key)
    elif args.command == '--version':
        return version_command()
    else:
        parser.print_help()

def process_command(bvid):
    """处理视频命令"""
    # 检查API密钥是否已配置
    api_key = get_api_key()
    if not api_key:
        print("错误: 未找到API密钥，请先运行 'haikubot config --key=YOUR_API_KEY' 配置API密钥")
        return 1
    
    try:
        result = process_video(bvid, verbose=True)
        print("\n俳句结果:")
        print("="*50)
        print(result["haiku"])
        print("="*50)
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1

def config_command(api_key):
    """配置API密钥命令"""
    if api_key:
        save_api_key(api_key)
        print("API密钥已保存")
        return 0
    else:
        current_key = get_api_key()
        if current_key:
            masked_key = current_key[:4] + '*' * (len(current_key) - 8) + current_key[-4:]
            print(f"当前API密钥: {masked_key}")
        else:
            print("未配置API密钥")
        return 0

def version_command():
    """显示版本信息命令"""
    from . import __version__
    print(f"HaikuBot v{__version__}")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 