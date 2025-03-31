#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
热搜预测系统启动脚本
"""

import os
import sys
import subprocess
import time
import requests

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import requests
        import bs4
        import apscheduler
        import dotenv
        import pytz
        print("所有依赖已安装")
        return True
    except ImportError as e:
        print(f"依赖检查失败: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("依赖安装完成")

def test_backend_connection(port=5000, retries=5, delay=2):
    """测试后端连接"""
    url = f"http://localhost:{port}"
    for i in range(retries):
        try:
            print(f"测试后端连接 (尝试 {i+1}/{retries})...")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"后端连接成功！响应: {response.json()}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"未连接到后端，{delay}秒后重试...")
        time.sleep(delay)
    
    print("无法连接到后端服务")
    return False

def run_backend():
    """运行后端服务"""
    os.chdir("backend")
    print("启动后端服务...")
    
    # 检查.env文件
    if not os.path.exists(".env"):
        print("警告: .env 文件不存在，将使用默认配置")
        # 创建一个最小的.env文件
        with open(".env", "w", encoding="utf-8") as f:
            f.write("PORT=5000\nDEBUG=True\n")
    
    # 打印当前工作目录和Python路径
    print(f"当前工作目录: {os.getcwd()}")
    print(f"使用Python: {sys.executable}")
    
    # 尝试使用不同的方法运行后端
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务启动
        time.sleep(3)
        
        # 测试服务连接
        if not test_backend_connection():
            print("后端服务可能未正确启动，请检查输出:")
            for i, line in enumerate(process.stdout):
                if i < 20:  # 只打印前20行
                    print(f"> {line.strip()}")
                else:
                    print("...")
                    break
            
            # 尝试终止进程
            process.terminate()
            return False
            
        # 持续打印输出
        for line in process.stdout:
            print(line.strip())
            
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return False
        
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("热搜预测系统启动工具")
    print("=" * 50)
    
    # 检查环境
    print(f"使用的Python: {sys.executable}")
    print(f"Python版本: {sys.version}")
    
    # 检查和安装依赖
    if not check_dependencies():
        print("尝试安装依赖...")
        install_dependencies()
        if not check_dependencies():
            print("依赖安装失败，请手动安装依赖")
            return
    
    # 检查 .env 文件
    if not os.path.exists("backend/.env"):
        print("警告: backend/.env 文件不存在")
        create_env = input("是否创建 .env 文件? (y/n): ")
        if create_env.lower() == 'y':
            api_key = input("请输入DeepSeek API密钥: ")
            with open("backend/.env", "w", encoding="utf-8") as f:
                f.write(f"# DeepSeek API密钥\n")
                f.write(f"DEEPSEEK_API_KEY={api_key}\n\n")
                f.write(f"# 服务器设置\n")
                f.write(f"PORT=5000\n")
                f.write(f"DEBUG=True\n\n")
                f.write(f"# 定时任务设置\n")
                f.write(f"SCRAPER_INTERVAL_HOURS=1\n")
                f.write(f"PREDICTION_HOUR=23\n")
                f.write(f"PREDICTION_MINUTE=0\n")
            print(".env 文件已创建")
    
    # 运行服务
    success = run_backend()
    if not success:
        print("\n后端服务未能成功启动，请检查错误信息")
        print("您可以尝试手动运行 'cd backend && python app.py'")
    
    print("\n服务已退出")

if __name__ == "__main__":
    main()