#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "=== 热搜预测系统启动脚本 ==="

# 检查Python环境
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "错误: 未找到Python解释器，请安装Python 3.7+"
    exit 1
fi

# 检查pip
if ! command -v pip &>/dev/null && ! command -v pip3 &>/dev/null; then
    echo "错误: 未找到pip，请安装pip"
    exit 1
fi

# 询问用户是否安装依赖
read -p "是否安装项目依赖? (y/n): " install_deps
if [[ "$install_deps" == "y" || "$install_deps" == "Y" ]]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 询问DeepSeek API密钥
read -p "请输入DeepSeek API密钥 (如果已设置环境变量可跳过): " api_key
if [[ ! -z "$api_key" ]]; then
    export DEEPSEEK_API_KEY=$api_key
    echo "已设置API密钥"
fi

# 启动后端服务
echo "启动后端服务..."
cd backend
$PYTHON app.py &
backend_pid=$!

echo "后端服务已启动，PID: $backend_pid"
echo "请在浏览器中打开 frontend/public/index.html 访问前端页面"
echo "按 Ctrl+C 停止服务"

# 捕获 SIGINT 信号 (Ctrl+C)
trap "echo '正在停止服务...'; kill $backend_pid; echo '服务已停止'; exit 0" INT

# 保持脚本运行
wait $backend_pid 