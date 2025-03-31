import requests
from bs4 import BeautifulSoup
import re
import time
import random

def fetch_tophub_data():
    """
    抓取 https://tophub.today/ 网站数据，按科技、职场、AI新闻分类
    
    返回:
        dict: 包含分类数据的字典，格式为 {"科技": [...], "职场": [...], "AI新闻": [...]}
    """
    # 设置请求头模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    result = {
        "科技": [],
        "职场": [],
        "AI新闻": []
    }
    
    try:
        # 获取主页内容
        url = "https://tophub.today/"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 使用Beautiful Soup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有内容块
        content_blocks = soup.find_all('div', class_='cc-cd')
        
        # 定义更详细的分类关键词
        category_keywords = {
            "科技": ['科技', '数码', 'IT', '互联网', '手机', '电脑', '硬件', '软件', '编程', '开发', '技术', '创新'],
            "职场": ['职场', '工作', '就业', '招聘', '简历', '求职', '薪资', '加班', '办公', '员工', '人才', '升职', '跳槽'],
            "AI新闻": ['AI', '人工智能', '机器学习', '深度学习', '神经网络', 'ChatGPT', 'GPT', '大模型', '智能', '算法', '自然语言处理', '计算机视觉']
        }
        
        # 遍历内容块，按类别提取信息
        for block in content_blocks:
            # 获取类别名称
            category_element = block.find('div', class_='cc-cd-lb')
            if not category_element:
                continue
                
            category_title = category_element.get_text(strip=True)
            
            # 根据类别名称进行分类
            target_category = None
            for category, keywords in category_keywords.items():
                if any(keyword in category_title for keyword in keywords):
                    target_category = category
                    break
                
            if target_category:
                # 查找该类别下的所有条目
                items = block.find_all('div', class_='cc-cd-cb-l')
                if not items and block.find('div', class_='cc-cd-cb'):
                    items = [block.find('div', class_='cc-cd-cb')]
                    
                # 如果找到了类别下的条目
                if items:
                    for item in items:
                        # 查找所有链接
                        links = item.find_all('a')
                        for link in links:
                            title = link.get_text(strip=True)
                            href = link.get('href', '')
                            if title and href and href.startswith('http'):
                                # 添加到对应类别
                                result[target_category].append({
                                    "title": title,
                                    "url": href
                                })
            
            # 短暂延迟，避免过快请求
            time.sleep(random.uniform(0.1, 0.3))
        
        # 如果某些类别数据不足，从其他类别中根据关键词提取
        if any(len(items) < 5 for category, items in result.items()):
            # 将所有抓取到的条目放入一个临时列表
            all_items = []
            for category, items in result.items():
                all_items.extend(items)
            
            # 对于数据不足的类别，从all_items中寻找相关的条目
            for category, items in result.items():
                if len(items) < 5:
                    keywords = category_keywords[category]
                    for item in all_items:
                        if item not in items:  # 避免重复
                            title = item["title"].lower()
                            # 如果标题中包含该类别的关键词，则添加到该类别
                            if any(keyword.lower() in title for keyword in keywords):
                                result[category].append(item)
        
        # 限制每个类别最多20条记录
        for category in result:
            result[category] = result[category][:20]
                
    except Exception as e:
        print(f"抓取数据时出错: {str(e)}")
    
    return result

if __name__ == '__main__':
    # 测试函数
    data = fetch_tophub_data()
    for category, items in data.items():
        print(f"{category}: {len(items)} 条")
        for i, item in enumerate(items[:3]):  # 只打印前3条作为示例
            print(f"  {i+1}. {item['title']} - {item['url']}") 