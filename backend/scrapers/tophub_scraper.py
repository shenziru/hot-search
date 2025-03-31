#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TopHub爬虫
负责抓取今日热榜(tophub.today)的科技相关数据
"""

import requests
import logging
import random
import time
from bs4 import BeautifulSoup

logger = logging.getLogger('tophub_scraper')

class TopHubScraper:
    """TopHub爬虫类"""
    
    def __init__(self):
        self.base_url = "https://tophub.today"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://tophub.today/"
        }
        self.tech_nodes = {
            "36Kr": "/n/Q1Vd5Ko85R",
            "虎嗅网": "/n/74Kvx59dkx",
            "少数派": "/n/Y2KeDGQdNp",
            "FreeBuf": "/n/NX5pOXVzB7"
        }
    
    def get_tech_news(self):
        """获取科技新闻数据"""
        results = []
        
        # 随机选择两个科技媒体抓取
        selected_nodes = random.sample(list(self.tech_nodes.items()), min(2, len(self.tech_nodes)))
        
        for source_name, node_url in selected_nodes:
            try:
                logger.info(f"开始抓取{source_name}热榜数据")
                url = f"{self.base_url}{node_url}"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"抓取{source_name}返回状态码: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select(".cc-cd-cb-l a")
                
                for i, item in enumerate(items[:15]):  # 只取前15条
                    title = item.text.strip()
                    if not title:
                        continue
                        
                    # 清理标题中的序号和多余空格
                    title = title.split(".", 1)[-1].strip() if "." in title else title
                    
                    link = item.get("href", "")
                    # 确保链接是完整的URL
                    if link and not (link.startswith("http://") or link.startswith("https://")):
                        if link.startswith("/"):
                            link = f"{self.base_url}{link}"
                        else:
                            link = f"https://{link}"
                    
                    # 获取热度值
                    hot_elem = item.select_one(".cc-cd-cb-ll")
                    hot = hot_elem.text.strip() if hot_elem else "0"
                    try:
                        hot_value = int(hot.replace("万", "0000").replace("k", "000").replace("+", ""))
                    except ValueError:
                        hot_value = i * 1000  # 如果无法解析，则使用位置作为热度
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "hot": hot_value,
                        "source": source_name
                    })
                
                logger.info(f"成功抓取{source_name}热榜数据: {len(results)}条")
                
                # 随机休眠，避免请求过快
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"抓取{source_name}热榜异常: {e}")
        
        # 按热度排序
        results.sort(key=lambda x: x.get("hot", 0), reverse=True)
        return results
        
    def get_all_tech_data(self):
        """获取所有科技数据"""
        return self.get_tech_news()


# 创建单例
tophub_scraper = TopHubScraper()

# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = TopHubScraper()
    data = scraper.get_all_tech_data()
    print(f"抓取到 {len(data)} 条科技新闻:")
    for i, item in enumerate(data):
        print(f"{i+1}. {item['title']} - 热度:{item.get('hot', 0)} - 来源:{item.get('source', '未知')}") 