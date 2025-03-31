# 热搜预测系统

这是一个基于Python和JavaScript开发的热搜预测系统，能够抓取热门网站的信息，并利用人工智能预测未来可能的热点话题。

## 功能特点

1. **数据抓取**：定时抓取 [Today热榜](https://tophub.today/) 的信息，按照科技、职场、AI新闻分类展示
2. **热点预测**：每天晚上11点自动分析当天热搜数据，预测第二天可能的热点话题
3. **标题生成**：为每个预测的热点自动生成3个创意标题
4. **美观界面**：响应式设计，支持各种设备浏览

## 技术栈

- **后端**：
  - Python Flask (Web框架)
  - BeautifulSoup (网页解析)
  - APScheduler (定时任务)
  - DeepSeek API (AI分析与预测)

- **前端**：
  - HTML5/CSS3
  - JavaScript (原生)
  - Bootstrap 5 (UI框架)
  - Font Awesome (图标)

## 系统要求

- Python 3.7+
- 网络连接
- DeepSeek API密钥（用于AI预测功能）

## 快速启动

最简单的方法是使用我们的全新一键启动脚本：

```bash
# 给脚本添加执行权限
chmod +x start_all.py

# 运行一键启动脚本（同时启动前端和后端）
./start_all.py
```

脚本会自动检查依赖、设置环境变量、启动后端服务，并在浏览器中打开前端页面。

## 详细安装步骤

如果您想手动安装和启动系统，请按照以下步骤操作：

1. 克隆仓库到本地：
   ```bash
   git clone <仓库地址>
   cd hot_key
   ```

2. 安装后端依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   ```bash
   # 复制示例配置文件
   cp backend/.env.example backend/.env
   
   # 编辑配置文件，填入您的DeepSeek API密钥
   vim backend/.env
   ```

4. 启动服务：
   - 使用单独的启动脚本：
     - 后端：`./run.py`
     - 前端：`./serve_frontend.py`
   
   - 或手动启动：
     ```bash
     # 启动后端
     cd backend
     python app.py
     
     # 启动前端（新终端）
     python -m http.server 8000 --directory frontend
     ```

5. 访问前端页面：在浏览器中打开 `http://localhost:8000/public/` 

## 环境变量配置

在 `backend/.env` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | (必填) |
| `PORT` | 服务器端口 | 5000 |
| `DEBUG` | 调试模式 | True |
| `SCRAPER_INTERVAL_HOURS` | 抓取数据的间隔时间(小时) | 1 |
| `PREDICTION_HOUR` | 生成预测的小时 | 23 |
| `PREDICTION_MINUTE` | 生成预测的分钟 | 0 |

## 目录结构

```
hot_key/
│
├── backend/              # 后端代码
│   ├── app.py            # Flask应用主文件
│   ├── scraper/          # 数据抓取模块
│   │   └── tophub_scraper.py
│   ├── api/              # API调用模块
│   │   └── deepseek_api.py
│   ├── data/             # 数据存储目录
│   └── .env              # 环境变量配置
│
├── frontend/             # 前端代码
│   ├── public/           # 静态资源
│   │   └── index.html    # 主页面
│   └── src/              # 源代码
│       ├── app.js        # 前端逻辑
│       └── styles.css    # 样式表
│
├── run.py                # 后端启动助手
├── serve_frontend.py     # 前端服务器
├── start_all.py          # 一键启动脚本
└── requirements.txt      # 项目依赖
```

## 使用说明

1. 启动后端服务后，系统会自动抓取一次当前热搜数据
2. 按照配置的时间间隔（默认每小时）自动更新热搜数据
3. 每天配置的时间点（默认23:00）会自动分析当天数据并生成明日热点预测
4. 访问前端页面可以查看当前热搜和预测结果
5. 点击"刷新数据"按钮可以手动触发数据刷新

## 故障排除

1. **依赖安装问题**
   - 使用 `./run.py` 启动，它会自动检查并安装缺失的依赖
   - 确保使用的是Python 3.7+版本
   - 如果出现权限问题，尝试使用 `pip install --user -r requirements.txt`

2. **无法连接到DeepSeek API**
   - 检查您的API密钥是否正确
   - 检查网络连接是否正常

3. **网页抓取失败**
   - TopHub网站可能已更改结构，需要更新抓取逻辑
   - 检查是否被目标网站限制访问

4. **前端无法加载数据**
   - 确保后端服务正在运行
   - 检查浏览器控制台是否有错误信息
   - 确认API端点URL是否正确（默认为http://localhost:5000/api）

## 许可证

[MIT License](LICENSE) 