import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API设置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def predict_hot_topics(current_data):
    """
    使用DeepSeek API预测明日热点话题并生成标题
    
    参数:
        current_data (dict): 当前的热搜数据，格式为 {"科技": [...], "职场": [...], "AI新闻": [...]}
    
    返回:
        list: 预测的热点话题列表，每个话题包含主题和三个候选标题
    """
    if not DEEPSEEK_API_KEY:
        print("警告: 未设置DeepSeek API密钥，无法进行预测")
        return []
    
    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    # 准备明天的日期
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y年%m月%d日")
    
    # 构建提示词
    prompt = f"""
    基于以下当前热搜数据，预测{tomorrow}可能的热点话题。
    
    当前热搜数据:
    """
    
    # 添加当前热搜数据
    for category, items in current_data.items():
        prompt += f"\n{category}类别热搜:\n"
        for i, item in enumerate(items[:10]):  # 每个类别只使用前10条
            prompt += f"{i+1}. {item['title']}\n"
    
    prompt += f"""
    请分析上述数据，预测{tomorrow}可能会成为热点的5个话题，并为每个话题生成3个吸引人的标题。
    
    返回格式要求为JSON格式，如下所示:
    [
      {{
        "topic": "话题1描述",
        "titles": ["标题1", "标题2", "标题3"]
      }},
      {{
        "topic": "话题2描述",
        "titles": ["标题1", "标题2", "标题3"]
      }},
      ...
    ]
    
    请确保返回的是有效的JSON格式数据，不要包含任何额外的说明或注释。
    """
    
    # 准备API请求数据
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        # 发送请求
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 提取JSON部分
        try:
            # 寻找JSON部分
            json_start = ai_response.find("[")
            json_end = ai_response.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                predictions = json.loads(json_str)
                return predictions
            else:
                print("无法从API响应中提取JSON数据")
                return []
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            print(f"原始响应: {ai_response}")
            return []
            
    except Exception as e:
        print(f"调用DeepSeek API时出错: {str(e)}")
        return []

def test_api_with_mock_data():
    """测试函数，使用模拟数据"""
    mock_data = {
        "科技": [
            {"title": "苹果发布新一代iPhone", "url": "https://example.com/1"},
            {"title": "华为推出新款折叠屏手机", "url": "https://example.com/2"}
        ],
        "职场": [
            {
                "title": "大厂招聘回暖，AI岗位需求激增200%",
                "reason": "随着AI技术的快速发展和商业化应用的扩大，大型科技公司对AI人才的需求将继续增长。这一趋势反映了就业市场的结构性变化，也将引导更多年轻人转向AI相关专业学习。"
            },
            {
                "title": "远程办公新政出台，三成企业将采用混合工作模式",
                "reason": "疫情后，远程和混合办公模式已成为新常态。政府和企业可能出台新的政策来规范和支持这种工作方式，平衡效率和员工满意度，这将成为职场热议话题。"
            },
            {
                "title": "职场\"35岁现象\"引发社会关注，多地出台应对政策",
                "reason": "年龄歧视问题一直是职场热点话题，特别是科技行业的\"35岁危机\"。随着人口老龄化加速和退休年龄延长讨论，社会对中年职场人的关注度会提高，可能促使政策调整和企业文化变革。"
            }
        ],
        "AI新闻": [
            {"title": "GPT-5即将发布", "url": "https://example.com/5"},
            {"title": "AI绘画技术取得突破", "url": "https://example.com/6"}
        ]
    }
    
    predictions = predict_hot_topics(mock_data)
    print(json.dumps(predictions, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # 测试API调用
    test_api_with_mock_data() 