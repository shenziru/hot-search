import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# 添加项目根目录到系统路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 导入自定义模块
from backend.scrapers.manager import get_all_data, get_category_data

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app')

# 创建Flask应用
app = Flask(__name__, static_folder="static")
CORS(app)  # 允许跨域请求

# 缓存数据和更新时间
cache = {
    "hot_data": {},
    "predictions": [],
    "last_update": None,
    "prediction_date": datetime.now().strftime("%Y-%m-%d")
}

# 创建静态目录
os.makedirs(app.static_folder, exist_ok=True)

@app.route("/")
def index():
    """首页"""
    return jsonify({
        "status": "ok",
        "message": "Hot Key Prediction API is running",
        "version": "1.0.0"
    })

@app.route("/api/hot_data")
def hot_data():
    """获取热搜数据"""
    global cache
    
    # 如果缓存过期或者强制更新
    force_update = request.args.get("force", "").lower() in ["true", "1", "yes"]
    
    if force_update or cache["last_update"] is None or \
       (datetime.now() - cache["last_update"]) > timedelta(minutes=30):
        try:
            logger.info("开始获取最新热搜数据")
            
            # 使用新的爬虫管理器获取数据
            hot_data = get_all_data(force_update=force_update)
            
            if hot_data:
                cache["hot_data"] = hot_data
                cache["last_update"] = datetime.now()
                logger.info(f"成功获取热搜数据: {sum(len(data) for data in hot_data.values())} 条")
            else:
                logger.warning("获取热搜数据为空")
        except Exception as e:
            logger.error(f"获取热搜数据异常: {e}")
            # 出错时返回缓存数据
    
    return jsonify(cache["hot_data"])

@app.route("/api/predictions")
def predictions():
    """获取预测数据"""
    global cache
    
    # 如果还没有预测数据，生成一些示例
    if not cache["predictions"]:
        create_example_predictions()
    
    return jsonify({
        "predictions": cache["predictions"],
        "date": cache["prediction_date"]
    })

@app.route("/api/generate_predictions", methods=["POST"])
def generate_predictions():
    """生成预测"""
    global cache
    
    try:
        # 从请求中获取热搜数据，如果没有则使用最新数据
        data = request.get_json() or {}
        hot_data = data.get("hot_data", cache["hot_data"])
        
        # 实际项目中这里应该调用模型生成预测
        # 这里简单实现，随机选取一些热搜作为预测
        import random
        
        predictions = []
        categories = list(hot_data.keys())
        
        # 为每个类别生成一些预测
        for i, category in enumerate(categories):
            items = hot_data.get(category, [])
            if not items:
                continue
                
            # 随机选择3个热搜
            selected_items = random.sample(items, min(3, len(items)))
            
            for j, item in enumerate(selected_items):
                title = item.get("title", "")
                url = item.get("url", "")
                hot = item.get("hot", 0)
                source = item.get("source", "未知")
                
                predictions.append({
                    "category": category,
                    "topic": f"话题{i+1}-{j+1}",
                    "title": title,
                    "reason": f"该话题在{source}平台热度达到{hot}，是{category}领域的热点内容",
                    "urls": [url] if url else [],
                    "titles": [
                        f"{title} - 明天会更火爆",
                        f"{title} - 持续发酵中",
                        f"{title} - 热度不减"
                    ]
                })
        
        # 更新缓存
        cache["predictions"] = predictions
        cache["prediction_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # 保存预测结果到文件
        save_predictions_to_file(predictions)
        
        return jsonify({
            "success": True,
            "message": f"成功生成 {len(predictions)} 条预测",
            "predictions": predictions,
            "date": cache["prediction_date"]
        })
    except Exception as e:
        logger.error(f"生成预测异常: {e}")
        return jsonify({
            "success": False,
            "message": f"生成预测失败: {str(e)}"
        }), 500

def create_example_predictions():
    """创建示例预测数据"""
    global cache
    
    # 示例预测数据
    predictions = [
        {
            "category": "科技",
            "topic": "话题1",
            "title": "苹果新品发布会定档 华为Mate60销量大增",
            "reason": "两大科技巨头在同一时间推出新品，引发用户关注",
            "urls": ["https://example.com/news1"],
            "titles": [
                "苹果华为正面交锋：一场科技霸主之争",
                "高端手机市场洗牌：谁能夺得市场主导权？",
                "国产手机能否真正撼动苹果地位？"
            ]
        },
        {
            "category": "AI工具",
            "topic": "话题2",
            "title": "AI图像生成模型再突破 艺术创作门槛大幅降低",
            "reason": "最新一代AI绘画模型让普通人也能创作专业级艺术作品",
            "urls": ["https://example.com/news2"],
            "titles": [
                "AI创意革命：人人都能成为艺术家",
                "传统艺术行业面临挑战：AI能否取代人类创造力？",
                "如何利用AI工具增强艺术表达？"
            ]
        },
        {
            "category": "大厂八卦职场新闻",
            "topic": "话题3",
            "title": "某互联网大厂裁员风波持续发酵",
            "reason": "多位员工在社交平台分享裁员经历，引发广泛关注",
            "urls": ["https://example.com/news3"],
            "titles": [
                "大厂裁员内幕：谁是最后的赢家？",
                "经济下行期，互联网从业者该如何自保？",
                "裁员潮背后：中国互联网行业进入新阶段"
            ]
        }
    ]
    
    cache["predictions"] = predictions
    cache["prediction_date"] = datetime.now().strftime("%Y-%m-%d")
    
    # 保存预测结果到文件
    save_predictions_to_file(predictions)

def save_predictions_to_file(predictions):
    """保存预测结果到文件"""
    try:
        # 确保静态目录存在
        os.makedirs(app.static_folder, exist_ok=True)
        
        # 保存预测结果
        prediction_file = os.path.join(app.static_folder, "predictions.json")
        with open(prediction_file, "w", encoding="utf-8") as f:
            json.dump({
                "predictions": predictions,
                "date": cache["prediction_date"],
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"预测结果已保存到文件: {prediction_file}")
    except Exception as e:
        logger.error(f"保存预测结果到文件失败: {e}")

# 启动时加载数据
@app.before_first_request
def initialize():
    """应用启动时初始化数据"""
    try:
        # 尝试加载预测数据
        prediction_file = os.path.join(app.static_folder, "predictions.json")
        if os.path.exists(prediction_file):
            with open(prediction_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                cache["predictions"] = data.get("predictions", [])
                cache["prediction_date"] = data.get("date", datetime.now().strftime("%Y-%m-%d"))
                logger.info(f"从文件加载了 {len(cache['predictions'])} 条预测")
        
        # 如果没有预测数据，创建示例数据
        if not cache["predictions"]:
            create_example_predictions()
            
        # 初始加载热搜数据
        hot_data()
    except Exception as e:
        logger.error(f"初始化数据异常: {e}")

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "").lower() in ["true", "1", "yes"]
    
    # 启动初始化
    # Flask 2.0以下版本不会自动调用before_first_request
    # 所以我们手动调用一次
    with app.app_context():
        initialize()
    
    app.run(host=host, port=port, debug=debug) 