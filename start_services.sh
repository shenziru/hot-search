#!/bin/bash

# 热搜预测系统服务启动脚本
echo "=====================================================
 热搜预测系统服务启动
 当前时间: $(date '+%Y-%m-%d %H:%M:%S')
====================================================="

# 检查是否安装了必要的软件包
check_dependency() {
  if ! command -v $1 &> /dev/null; then
    echo "❌ $1 未安装。请安装后再试。"
    return 1
  else
    echo "✅ $1 已安装"
    return 0
  fi
}

echo "检查依赖项..."
check_dependency python3 || { echo "请安装Python 3"; exit 1; }
check_dependency npm || { echo "请安装Node.js和npm"; exit 1; }

# 确定项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "项目目录: $PROJECT_DIR"

# 启动后端服务
start_backend() {
  echo "
📡 启动后端服务..."
  cd "$PROJECT_DIR"
  
  # 检查是否存在.env文件
  if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    echo "警告: 未找到.env文件，创建默认配置文件"
    echo "DEEPSEEK_API_KEY=your_api_key_here" > "$PROJECT_DIR/backend/.env"
    echo "请修改 backend/.env 文件并设置您的DeepSeek API密钥"
  fi
  
  # 检查虚拟环境
  if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
    echo "安装后端依赖..."
    source "$PROJECT_DIR/venv/bin/activate"
    pip install -r "$PROJECT_DIR/backend/requirements.txt"
  else
    source "$PROJECT_DIR/venv/bin/activate"
  fi
  
  # 启动后端服务
  cd "$PROJECT_DIR/backend"
  python app.py &
  BACKEND_PID=$!
  echo "后端服务已启动 (PID: $BACKEND_PID)"
  
  # 等待后端启动
  echo "等待后端服务就绪..."
  sleep 3
  
  # 测试后端连接
  MAX_RETRIES=5
  RETRY_COUNT=0
  
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/ > /dev/null; then
      echo "✅ 后端服务已就绪"
      break
    else
      RETRY_COUNT=$((RETRY_COUNT+1))
      if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ 后端服务启动失败，请检查日志"
        # 打印最后的日志
        echo "最后10行日志:"
        tail -n 10 "$PROJECT_DIR/backend/app.log" 2>/dev/null || echo "无法读取日志文件"
      else
        echo "等待后端就绪... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
      fi
    fi
  done
}

# 启动前端服务
start_frontend() {
  echo "
🖥️ 启动前端服务..."
  cd "$PROJECT_DIR/frontend"
  
  # 检查node_modules
  if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "安装前端依赖..."
    npm install
  fi
  
  # 启动前端服务
  npm start &
  FRONTEND_PID=$!
  echo "前端服务已启动 (PID: $FRONTEND_PID)"
  
  # 等待前端启动
  echo "等待前端服务就绪..."
  sleep 5
  
  # 尝试打开浏览器
  if command -v open &> /dev/null; then
    open http://localhost:3000
  elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
  else
    echo "请在浏览器中访问: http://localhost:3000"
  fi
}

# 记录PID以便后续可能的停止操作
save_pids() {
  echo "$BACKEND_PID" > "$PROJECT_DIR/.backend_pid"
  echo "$FRONTEND_PID" > "$PROJECT_DIR/.frontend_pid"
  echo "
服务PID已保存到项目目录。要停止服务，请运行:
  kill \$(cat $PROJECT_DIR/.backend_pid) \$(cat $PROJECT_DIR/.frontend_pid)"
}

# 主程序
start_backend
start_frontend
save_pids

echo "
🚀 所有服务已启动!
📊 前端访问地址: http://localhost:3000
🔄 后端API地址: http://localhost:5000

提示: 按Ctrl+C 终止此脚本不会停止服务!
要停止服务，请运行:
  kill \$(cat $PROJECT_DIR/.backend_pid) \$(cat $PROJECT_DIR/.frontend_pid)
"

# 保持脚本运行，以便查看日志
echo "显示日志输出 (按Ctrl+C退出日志查看)..."
tail -f "$PROJECT_DIR/backend/app.log" 2>/dev/null || echo "等待日志文件生成..." 