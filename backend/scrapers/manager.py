#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬虫管理器
负责调度和管理各个爬虫模块
"""

import os
import time
import json
import logging
from pathlib import Path

from .maimai_scraper import MaimaiScraper
from .sspai_scraper import SSPAIScraper
from .tophub_scraper import TopHubScraper
from backend.config.data_sources import (
    DATA_SOURCE_MAPPING, 
    BASE_CONFIG, 
    ROOT_DIR
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scraper_manager')

class ScraperManager:
    """爬虫管理类"""
    
    def __init__(self):
        self.data_source_mapping = DATA_SOURCE_MAPPING
        self.base_config = BASE_CONFIG
        self.cache_dir = ROOT_DIR / 'temp' / 'cache'
        self.last_update_file = ROOT_DIR / 'temp' / 'last_update.json'
        
        # 确保缓存目录存在
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
            
        # 加载上次更新时间
        self.last_update_times = self._load_last_update_times()
        
        # 初始化爬虫实例
        self.scrapers = {
            'maimai': MaimaiScraper(),
            'sspai': SSPAIScraper(),
            'tophub': TopHubScraper(),
        }
        
    def _load_last_update_times(self):
        """加载上次更新时间"""
        if os.path.exists(self.last_update_file):
            try:
                with open(self.last_update_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载上次更新时间失败: {e}")
        return {}
        
    def _save_last_update_times(self):
        """保存上次更新时间"""
        try:
            with open(self.last_update_file, 'w', encoding='utf-8') as f:
                json.dump(self.last_update_times, f)
        except Exception as e:
            logger.error(f"保存上次更新时间失败: {e}")
            
    def _load_cache(self, category):
        """从缓存加载数据"""
        cache_file = self.cache_dir / f"{category}.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载缓存数据失败: {e}")
        return []
        
    def _save_cache(self, category, data):
        """保存数据到缓存"""
        cache_file = self.cache_dir / f"{category}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存缓存数据失败: {e}")
            
    def need_update(self, category):
        """判断类别是否需要更新"""
        if category not in self.data_source_mapping:
            return True
            
        last_update = self.last_update_times.get(category, 0)
        return self.data_source_mapping[category]['need_update'](last_update)
        
    def update_timestamp(self, category):
        """更新类别的最后更新时间"""
        if category in self.data_source_mapping:
            self.last_update_times[category] = self.data_source_mapping[category]['update_timestamp']()
            self._save_last_update_times()
            
    def get_category_data(self, category, force_update=False):
        """获取指定类别的数据"""
        if category not in self.data_source_mapping:
            logger.error(f"未知类别: {category}")
            return []
            
        # 特殊处理科技类别，因为暂时没有对应的爬虫
        if category == '科技':
            logger.info(f"使用示例数据作为科技类别的数据")
            example_data = self._get_example_tech_data()
            return example_data
            
        # 判断是否需要更新
        if not force_update and not self.need_update(category):
            logger.info(f"类别 {category} 使用缓存数据")
            return self._load_cache(category)
            
        logger.info(f"开始抓取类别 {category} 的数据")
        
        # 获取数据源和对应的爬虫
        source_name = self.data_source_mapping[category]['source']
        scraper = self.scrapers.get(source_name)
        
        if not scraper:
            logger.error(f"未找到类别 {category} 对应的爬虫")
            return self._load_cache(category)  # 返回缓存数据
            
        # 根据不同的数据源类型，调用不同的方法
        data = []
        try:
            if source_name == 'maimai':
                data = scraper.get_all_hot_data()
            elif source_name == 'sspai':
                data = scraper.get_all_ai_tools()
            elif source_name == 'tophub':
                data = scraper.get_all_tech_data()
            else:
                logger.error(f"未知数据源类型: {source_name}")
                return self._load_cache(category)
                
            # 更新时间戳和缓存
            if data:
                self.update_timestamp(category)
                self._save_cache(category, data)
                logger.info(f"类别 {category} 抓取成功，获取到 {len(data)} 条数据")
            else:
                logger.warning(f"类别 {category} 抓取结果为空")
                
            return data
            
        except Exception as e:
            logger.error(f"抓取类别 {category} 数据异常: {e}")
            return self._load_cache(category)  # 出错时返回缓存数据
            
    def get_all_data(self, force_update=False):
        """获取所有类别的数据"""
        result = {}
        for category in self.data_source_mapping.keys():
            result[category] = self.get_category_data(category, force_update)
        return result
        
    def _get_example_tech_data(self):
        """生成示例科技数据"""
        return [
            {
                "title": "苹果发布会定档，将推出新一代M4芯片",
                "url": "https://example.com/news1",
                "hot": 9876,
                "source": "科技媒体"
            },
            {
                "title": "华为Mate70系列即将发布，预计搭载麒麟芯片",
                "url": "https://example.com/news2",
                "hot": 8765,
                "source": "科技媒体"
            },
            {
                "title": "特斯拉推出新型自动驾驶系统，精度提升50%",
                "url": "https://example.com/news3",
                "hot": 7654,
                "source": "科技媒体"
            },
            {
                "title": "谷歌DeepMind发布最新AI研究成果，突破多模态理解",
                "url": "https://example.com/news4",
                "hot": 6543,
                "source": "科技媒体"
            },
            {
                "title": "Meta发布新一代VR设备，更轻更强大",
                "url": "https://example.com/news5",
                "hot": 5432,
                "source": "科技媒体"
            },
            {
                "title": "微软发布Windows 11新版本，大幅提升AI功能",
                "url": "https://example.com/news6",
                "hot": 4321,
                "source": "科技媒体"
            },
            {
                "title": "苹果Vision Pro销量突破百万台",
                "url": "https://example.com/news7",
                "hot": 3210,
                "source": "科技媒体"
            },
            {
                "title": "亚马逊推出新型智能家居设备，集成大模型",
                "url": "https://example.com/news8",
                "hot": 2109,
                "source": "科技媒体"
            },
            {
                "title": "小米汽车SU7预订量超30万台",
                "url": "https://example.com/news9",
                "hot": 1987,
                "source": "科技媒体"
            },
            {
                "title": "NVIDIA发布新一代GPU，性能提升80%",
                "url": "https://example.com/news10",
                "hot": 1876,
                "source": "科技媒体"
            },
            {
                "title": "OpenAI推出最新版GPT-5模型，能力全面超越人类",
                "url": "https://example.com/news11",
                "hot": 1765,
                "source": "科技媒体"
            },
            {
                "title": "量子计算取得重大突破，IBM实现100量子比特稳定运行",
                "url": "https://example.com/news12",
                "hot": 1654,
                "source": "科技媒体"
            }
        ]
        
# 单例模式
scraper_manager = ScraperManager()

# 对外接口
def get_category_data(category, force_update=False):
    """获取指定类别的数据"""
    return scraper_manager.get_category_data(category, force_update)
    
def get_all_data(force_update=False):
    """获取所有类别的数据"""
    return scraper_manager.get_all_data(force_update)


# 测试代码
if __name__ == "__main__":
    # 测试获取各类别数据
    categories = list(DATA_SOURCE_MAPPING.keys())
    for category in categories:
        print(f"\n获取类别 {category} 的数据:")
        data = get_category_data(category, force_update=True)
        for i, item in enumerate(data[:5]):  # 只显示前5条
            print(f"{i+1}. {item['title']} - 热度:{item.get('hot', 0)} - 来源:{item.get('source', '未知')}")
        
    # 测试获取所有数据
    print("\n获取所有类别的数据:")
    all_data = get_all_data(force_update=False)  # 使用缓存
    for category, data in all_data.items():
        print(f"\n类别 {category} 数据 ({len(data)} 条):")
        for i, item in enumerate(data[:3]):  # 只显示前3条
            print(f"{i+1}. {item['title']}") 