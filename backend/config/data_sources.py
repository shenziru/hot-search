#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据源配置文件
用于配置各个热点数据源的抓取参数
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv(Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / '.env')

# 项目根目录
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 基础配置
BASE_CONFIG = {
    # 请求头
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # 请求超时（秒）
    'request_timeout': 10,
    
    # 请求重试次数
    'retry_times': 3,
    
    # 缓存时间（秒）
    'cache_time': 1800,  # 30分钟
}

# 脉脉配置
MAIMAI_CONFIG = {
    # 最大获取条目数
    'max_items': 20,
    
    # 登录信息
    'login': {
        'username': os.getenv('MAIMAI_USERNAME'),
        'password': os.getenv('MAIMAI_PASSWORD'),
        'cookie_path': str(ROOT_DIR / 'temp' / 'maimai_cookies.json'),
    },
    
    # 接口端点
    'endpoints': {
        # 热门话题
        'hot_topics': 'https://maimai.cn/api/feed/list?u=&page=0&channel=1&_csrf=',
        
        # 公司热榜
        'company_hot': 'https://maimai.cn/api/gossip/v2/hot_list?_csrf=',
        
        # 行业热榜
        'industry_hot': 'https://maimai.cn/api/gossip/v3/hot_subjects?domain=&_csrf=',
    },
    
    # 更新频率
    'update_interval': 3600,  # 1小时
}

# 少数派配置
SSPAI_CONFIG = {
    # 最大获取条目数
    'max_items': 20,
    
    # 接口端点
    'endpoints': {
        # AI工具标签页
        'ai_tools': '/tag/AI',
        
        # 文章API
        'api_articles': 'https://sspai.com/api/v1/articles?limit=20&offset=0&is_matrix=1&sort=matrix_at',
    },
    
    # 更新频率
    'update_interval': 7200,  # 2小时
}

# 科技媒体配置
TECH_MEDIA_CONFIG = {
    # 最大获取条目数
    'max_items': 20,
    
    # 接口端点
    'endpoints': {
        # 36氪
        '36kr': 'https://36kr.com/information/technology',
        
        # 爱范儿
        'ifanr': 'https://www.ifanr.com/category/ai',
    },
    
    # 更新频率
    'update_interval': 3600,  # 1小时
}

# TopHub配置
TOPHUB_CONFIG = {
    # 最大获取条目数
    'max_items': 20,
    
    # 接口端点
    'endpoints': {
        # 36Kr热榜
        '36kr': '/n/Q1Vd5Ko85R',
        
        # 虎嗅热榜
        'huxiu': '/n/74Kvx59dkx',
        
        # 少数派热榜
        'sspai': '/n/Y2KeDGQdNp',
        
        # FreeBuf热榜
        'freebuf': '/n/NX5pOXVzB7'
    },
    
    # 更新频率
    'update_interval': 3600,  # 1小时
}

# 数据源和功能映射关系
DATA_SOURCE_MAPPING = {
    '大厂八卦职场新闻': {
        'source': 'maimai',
        'need_update': lambda last_update: time.time() - last_update > MAIMAI_CONFIG['update_interval'],
        'update_timestamp': lambda: time.time(),
    },
    'AI工具': {
        'source': 'sspai',
        'need_update': lambda last_update: time.time() - last_update > SSPAI_CONFIG['update_interval'],
        'update_timestamp': lambda: time.time(),
    },
    '科技': {
        'source': 'tophub',
        'need_update': lambda last_update: time.time() - last_update > TOPHUB_CONFIG['update_interval'],
        'update_timestamp': lambda: time.time(),
    },
}

# 临时目录
TEMP_DIR = ROOT_DIR / 'temp'

# 确保临时目录存在
if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(parents=True)

# 确保cookie存储目录存在
cookie_dir = os.path.dirname(MAIMAI_CONFIG['login']['cookie_path'])
if not os.path.exists(cookie_dir):
    os.makedirs(cookie_dir) 