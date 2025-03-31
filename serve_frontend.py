#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
前端HTTP服务器
"""

import os
import sys
import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse

# 配置前端目录和端口
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def translate_path(self, path):
        """映射请求路径到实际文件路径"""
        path = super().translate_path(path)
        
        # 检查路径是相对于根目录还是相对于当前目录
        rel_path = os.path.relpath(path, os.getcwd())
        if rel_path.startswith('..'):
            # 如果路径跳出了当前目录，重置为前端目录
            return FRONTEND_DIR
        
        return path
    
    def end_headers(self):
        """添加CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

def main():
    """主函数"""
    # 切换到前端目录
    os.chdir(FRONTEND_DIR)
    
    # 创建服务器
    handler = MyHttpRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"前端服务器启动在 http://localhost:{PORT}")
    print(f"请访问 http://localhost:{PORT}/public/ 查看页面")
    print("按 Ctrl+C 停止服务器")
    
    # 打开浏览器
    webbrowser.open(f"http://localhost:{PORT}/public/")
    
    # 启动服务器
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    main() 