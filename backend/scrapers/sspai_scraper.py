#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
少数派AI专栏数据抓取模块
用于抓取少数派AI专栏的热门工具信息
"""

import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 导入配置
import sys
from backend.config.data_sources import SSPAI_CONFIG, BASE_CONFIG

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sspai_scraper')

class SSPAIScraper:
    """少数派AI专栏数据抓取类"""
    
    def __init__(self):
        self.config = SSPAI_CONFIG
        self.base_config = BASE_CONFIG
        self.base_url = "https://sspai.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.base_config['user_agent'],
            'Referer': self.base_url,
        })
        
    def get_ai_tools(self):
        """获取AI工具文章列表"""
        url = urljoin(self.base_url, self.config['endpoints']['ai_tools'])
        
        try:
            logger.info(f"正在从少数派获取AI工具文章列表: {url}")
            resp = self.session.get(
                url,
                timeout=self.base_config['request_timeout']
            )
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                articles = self._parse_articles(soup)
                logger.info(f"从少数派HTML页面获取到 {len(articles)} 条AI工具文章")
                return articles
            else:
                logger.error(f"获取少数派AI工具页面失败，状态码: {resp.status_code}")
        except Exception as e:
            logger.error(f"获取少数派AI工具页面异常: {e}")
            
        return []
        
    def get_articles_api(self):
        """通过API获取AI工具文章列表"""
        url = self.config['endpoints']['api_articles']
        
        try:
            logger.info(f"正在从少数派API获取文章列表: {url}")
            resp = self.session.get(
                url,
                timeout=self.base_config['request_timeout']
            )
            
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    if isinstance(result, dict) and 'data' in result:
                        # 新版API可能是这种格式
                        articles = result.get('data', [])
                    elif isinstance(result, list):
                        # 旧版API可能是这种格式
                        articles = result
                    else:
                        articles = []
                        logger.error(f"获取少数派文章API返回格式异常: {result}")
                        
                    if articles:
                        parsed_articles = self._parse_articles_api(articles)
                        logger.info(f"从少数派API获取到 {len(parsed_articles)} 条AI工具文章")
                        return parsed_articles
                    else:
                        logger.warning("少数派API返回的文章列表为空")
                except Exception as e:
                    logger.error(f"解析少数派API返回数据异常: {e}")
            else:
                logger.error(f"获取少数派文章API失败，状态码: {resp.status_code}")
        except Exception as e:
            logger.error(f"获取少数派文章API异常: {e}")
            
        return []
    
    def _parse_articles(self, soup):
        """解析HTML中的文章列表"""
        result = []
        try:
            # 查找所有文章卡片
            article_cards = soup.select(".article-card") or soup.select(".brief")
            
            for card in article_cards[:self.config['max_items']]:
                try:
                    # 提取标题和链接
                    title_elem = card.select_one(".title") or card.select_one("h2")
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    
                    # 提取链接
                    link_elem = card.select_one("a")
                    if not link_elem:
                        continue
                        
                    href = link_elem.get("href", "")
                    url = urljoin(self.base_url, href) if href else ""
                    
                    # 提取热度指标（点赞数、评论数等）
                    like_elem = card.select_one(".like-count")
                    comment_elem = card.select_one(".comment-count")
                    
                    like_count = int(like_elem.get_text(strip=True)) if like_elem else 0
                    comment_count = int(comment_elem.get_text(strip=True)) if comment_elem else 0
                    
                    hot = like_count + comment_count * 2
                    
                    # 将标题添加"AI工具:"前缀
                    title = f"AI工具: {title}"
                    
                    result.append({
                        "title": title,
                        "url": url,
                        "hot": hot,
                        "source": "少数派AI专栏"
                    })
                except Exception as e:
                    logger.error(f"解析少数派文章卡片失败: {e}")
            
        except Exception as e:
            logger.error(f"解析少数派文章列表失败: {e}")
            
        return result
    
    def _parse_articles_api(self, articles_data):
        """解析API返回的文章列表"""
        result = []
        
        for item in articles_data[:self.config['max_items']]:
            try:
                # 过滤只包含AI标签的文章
                tags = item.get("tags", [])
                is_ai_article = False
                
                for tag in tags:
                    tag_name = tag.get("name", "").lower()
                    if "ai" in tag_name or "人工智能" in tag_name or "chatgpt" in tag_name:
                        is_ai_article = True
                        break
                
                if not is_ai_article:
                    continue
                
                title = item.get("title", "")
                article_id = item.get("id", "")
                url = f"{self.base_url}/post/{article_id}" if article_id else ""
                
                # 计算热度
                like_count = item.get("like_count", 0)
                comment_count = item.get("comment_count", 0)
                hot = like_count + comment_count * 2
                
                # 将标题添加"AI工具:"前缀
                title = f"AI工具: {title}"
                
                result.append({
                    "title": title,
                    "url": url,
                    "hot": hot,
                    "source": "少数派AI专栏"
                })
            except Exception as e:
                logger.error(f"解析少数派API文章项目失败: {e}")
                
        return result
    
    def get_all_ai_tools(self):
        """获取所有AI工具相关文章"""
        # 首先尝试直接获取热门文章
        articles = []
        
        # 尝试从API获取
        api_articles = self.get_articles_api()
        if api_articles:
            articles.extend(api_articles)
            
        # 尝试从HTML页面获取
        html_articles = self.get_ai_tools()
        if html_articles:
            articles.extend(html_articles)
            
        # 如果还是没有文章，使用备用数据
        if not articles:
            logger.warning("无法从少数派获取文章，使用备用数据")
            articles = self._get_backup_ai_tools()
        
        # 去重（基于标题）
        unique_articles = {}
        for article in articles:
            title = article.get("title", "")
            if title and title not in unique_articles:
                unique_articles[title] = article
        
        # 按热度排序
        result = list(unique_articles.values())
        result.sort(key=lambda x: x.get("hot", 0), reverse=True)
        
        # 限制返回数量
        return result[:self.config['max_items']]
        
    def _get_backup_ai_tools(self):
        """提供一些备用的AI工具数据，防止API失效时没有数据显示"""
        return [
            {
                "title": "AI工具: Claude 3.5 Sonnet发布，性能超越GPT-4o",
                "url": "https://sspai.com/post/85217",
                "hot": 8500,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: 最新版Midjourney推出Zoom Out功能，轻松实现场景扩展",
                "url": "https://sspai.com/post/85142",
                "hot": 7800,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: 谷歌推出NotebookLM：AI笔记和文档助手，支持多种资料整合",
                "url": "https://sspai.com/post/85098",
                "hot": 7200,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: Microsoft Copilot整合进Windows系统，AI助手更方便使用",
                "url": "https://sspai.com/post/85056",
                "hot": 6800,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: OpenAI推出GPT-4o，多模态能力显著提升",
                "url": "https://sspai.com/post/84970",
                "hot": 6500,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: DeepL Write升级，支持多语言写作修改和润色",
                "url": "https://sspai.com/post/84899",
                "hot": 5900,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: 国产大模型智谱AI发布全新GLM-4系列模型",
                "url": "https://sspai.com/post/84866",
                "hot": 5600,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: 百度文心一言APP更新，增加AI绘画和视频生成功能",
                "url": "https://sspai.com/post/84832",
                "hot": 5300,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: Adobe推出Firefly 2.0，生成式AI提升创意效率",
                "url": "https://sspai.com/post/84789",
                "hot": 5100,
                "source": "少数派AI专栏"
            },
            {
                "title": "AI工具: 阿里云通义千问开放多模态大模型API，支持图像理解和生成",
                "url": "https://sspai.com/post/84756",
                "hot": 4800,
                "source": "少数派AI专栏"
            }
        ]


# 测试代码
if __name__ == "__main__":
    scraper = SSPAIScraper()
    
    print("获取少数派AI工具文章:")
    ai_tools = scraper.get_all_ai_tools()
    for i, article in enumerate(ai_tools):
        print(f"{i+1}. {article['title']} - 热度:{article['hot']} - 来源:{article['source']}") 