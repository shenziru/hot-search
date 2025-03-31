#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动前端和后端服务
"""

import os
import sys
import subprocess
import threading
import time
import signal
import atexit

# 保存子进程引用
processes = []

def run_backend():
    """启动后端服务"""
    print("[后端] 正在启动...")
    backend_process = subprocess.Popen([sys.executable, "run.py"], 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)
    processes.append(backend_process)
    
    # 读取输出
    for line in backend_process.stdout:
        sys.stdout.write(f"[后端] {line}")
    
    # 进程结束
    backend_process.wait()
    print(f"[后端] 进程结束，返回码: {backend_process.returncode}")

def run_frontend():
    """启动前端服务"""
    print("[前端] 正在启动...")
    # 等待后端服务启动
    time.sleep(3)
    
    frontend_process = subprocess.Popen([sys.executable, "serve_frontend.py"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
    processes.append(frontend_process)
    
    # 读取输出
    for line in frontend_process.stdout:
        sys.stdout.write(f"[前端] {line}")
    
    # 进程结束
    frontend_process.wait()
    print(f"[前端] 进程结束，返回码: {frontend_process.returncode}")

def cleanup():
    """清理所有子进程"""
    print("\n正在停止所有服务...")
    for process in processes:
        if process.poll() is None:  # 如果进程还在运行
            process.terminate()
            process.wait(timeout=5)
    print("所有服务已停止")

def signal_handler(sig, frame):
    """处理终止信号"""
    cleanup()
    sys.exit(0)

def main():
    """主函数"""
    # 注册清理函数
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 50)
    print("热搜预测系统启动工具")
    print("=" * 50)
    print("启动后端和前端服务...")
    print("按 Ctrl+C 停止所有服务")
    
    # 创建线程启动服务
    backend_thread = threading.Thread(target=run_backend)
    frontend_thread = threading.Thread(target=run_frontend)
    
    # 设置为守护线程，这样主线程退出时它们也会退出
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    # 启动线程
    backend_thread.start()
    frontend_thread.start()
    
    # 等待线程结束
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main() 