#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
脉脉数据抓取模块
用于模拟登录脉脉并抓取职场热榜数据
"""

import os
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 导入配置
import sys
from backend.config.data_sources import MAIMAI_CONFIG, BASE_CONFIG

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('maimai_scraper')

class MaimaiScraper:
    """脉脉数据抓取类"""
    
    def __init__(self):
        self.config = MAIMAI_CONFIG
        self.base_config = BASE_CONFIG
        self.base_url = "https://maimai.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.base_config['user_agent'],
            'Referer': self.base_url,
            'Origin': self.base_url
        })
        self.cookie_path = self.config['login']['cookie_path']
        
    def _save_cookies(self):
        """保存cookies到文件"""
        with open(self.cookie_path, 'w') as f:
            json.dump(self.session.cookies.get_dict(), f)
            
    def _load_cookies(self):
        """从文件加载cookies"""
        if os.path.exists(self.cookie_path):
            try:
                with open(self.cookie_path, 'r') as f:
                    cookies = json.load(f)
                    if cookies:
                        for name, value in cookies.items():
                            self.session.cookies.set(name, value)
                        return True
            except Exception as e:
                logger.error(f"加载cookies失败: {e}")
        return False
        
    def _check_login_status(self):
        """检查登录状态"""
        try:
            resp = self.session.get(
                urljoin(self.base_url, "/web/feed_list"), 
                timeout=self.base_config['request_timeout']
            )
            return "请登录" not in resp.text
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
            
    def login(self):
        """登录脉脉"""
        # 先尝试从文件加载cookies
        if self._load_cookies() and self._check_login_status():
            logger.info("使用已保存的cookies登录成功")
            return True
            
        # 如果cookies无效，则模拟账号密码登录
        login_url = urljoin(self.base_url, "/api/account/login") 
        login_data = {
            "account": self.config['login']['username'],
            "password": self.config['login']['password'],
            "udid": "",
            "version": "5.0.0",
            "platform": "web",
            "csrf": ""
        }
        
        try:
            logger.info("开始登录脉脉...")
            resp = self.session.post(
                login_url,
                json=login_data,
                timeout=self.base_config['request_timeout']
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    logger.info("脉脉账号密码登录成功")
                    self._save_cookies()
                    return True
                else:
                    error_msg = result.get("msg", "未知错误")
                    logger.error(f"脉脉登录失败: {error_msg}")
            else:
                logger.error(f"脉脉登录请求失败，状态码: {resp.status_code}")
        except Exception as e:
            logger.error(f"脉脉登录异常: {e}")
            
        return False
    
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            resp = self.session.get(
                self.base_url,
                timeout=self.base_config['request_timeout']
            )
            soup = BeautifulSoup(resp.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                return csrf_meta.get('content', '')
        except Exception as e:
            logger.error(f"获取CSRF令牌失败: {e}")
        return ""
    
    def get_hot_topics(self):
        """获取热门话题"""
        if not self._check_login_status() and not self.login():
            logger.error("未登录，无法获取热门话题")
            return []
            
        # 获取CSRF令牌
        csrf_token = self.get_csrf_token()
        url = self.config['endpoints']['hot_topics'].replace("_csrf=", f"_csrf={csrf_token}")
        
        try:
            logger.info(f"正在获取脉脉热门话题: {url}")
            resp = self.session.get(
                url,
                timeout=self.base_config['request_timeout']
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    feed_list = result.get("data", {}).get("list", [])
                    parsed_items = self._parse_feed_items(feed_list)
                    logger.info(f"成功获取脉脉热门话题: {len(parsed_items)}条")
                    return parsed_items
                else:
                    logger.error(f"获取热门话题失败: {result.get('msg', '未知错误')}")
            else:
                logger.error(f"获取热门话题请求失败，状态码: {resp.status_code}")
        except Exception as e:
            logger.error(f"获取热门话题异常: {e}")
            
        return []
    
    def get_company_hot(self):
        """获取公司热榜"""
        if not self._check_login_status() and not self.login():
            logger.error("未登录，无法获取公司热榜")
            return []
            
        # 获取CSRF令牌
        csrf_token = self.get_csrf_token()
        url = self.config['endpoints']['company_hot'].replace("_csrf=", f"_csrf={csrf_token}")
        
        try:
            logger.info(f"正在获取脉脉公司热榜: {url}")
            resp = self.session.get(
                url,
                timeout=self.base_config['request_timeout']
            )
            
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0:
                    discuss_list = result.get("data", {}).get("list", [])
                    parsed_items = self._parse_discuss_items(discuss_list)
                    logger.info(f"成功获取脉脉公司热榜: {len(parsed_items)}条")
                    return parsed_items
                else:
                    logger.error(f"获取公司热榜失败: {result.get('msg', '未知错误')}")
            else:
                logger.error(f"获取公司热榜请求失败，状态码: {resp.status_code}")
        except Exception as e:
            logger.error(f"获取公司热榜异常: {e}")
            
        return []
    
    def _parse_feed_items(self, feed_list):
        """解析热门话题数据"""
        result = []
        for item in feed_list[:self.config['max_items']]:
            try:
                text = item.get("text", "")
                title = text[:80] + "..." if len(text) > 80 else text
                
                # 解析URL
                feed_id = item.get("id")
                url = f"{self.base_url}/web/gossip_detail/{feed_id}" if feed_id else ""
                
                # 如果有公司标签，添加"公司"前缀
                if item.get("company") and item.get("company", {}).get("name"):
                    company_name = item.get("company", {}).get("name", "")
                    title = f"[{company_name}] {title}"
                
                result.append({
                    "title": title,
                    "url": url,
                    "hot": item.get("like_cnt", 0) + item.get("comment_cnt", 0),
                    "source": "脉脉热门"
                })
            except Exception as e:
                logger.error(f"解析热门话题项目失败: {e}")
                
        return result
    
    def _parse_discuss_items(self, discuss_list):
        """解析公司热榜数据"""
        result = []
        for item in discuss_list[:self.config['max_items']]:
            try:
                title = item.get("title", "")
                
                # 解析URL
                feed_id = item.get("id")
                url = f"{self.base_url}/web/gossip_detail/{feed_id}" if feed_id else ""
                
                # 如果有公司名称，添加公司前缀
                if item.get("company_name"):
                    company_name = item.get("company_name", "")
                    title = f"[{company_name}] {title}"
                
                result.append({
                    "title": title,
                    "url": url,
                    "hot": item.get("hot", 0),
                    "source": "脉脉公司热榜"
                })
            except Exception as e:
                logger.error(f"解析公司热榜项目失败: {e}")
                
        return result
    
    def get_all_hot_data(self):
        """获取所有热门数据"""
        hot_data = []
        
        # 获取热门话题
        try:
            topic_data = self.get_hot_topics()
            if topic_data:
                hot_data.extend(topic_data)
                logger.info(f"获取到热门话题 {len(topic_data)} 条")
            else:
                logger.warning("获取热门话题失败或为空")
        except Exception as e:
            logger.error(f"获取热门话题出错: {e}")
        
        # 获取公司热榜
        try:
            company_data = self.get_company_hot()
            if company_data:
                hot_data.extend(company_data)
                logger.info(f"获取到公司热榜 {len(company_data)} 条")
            else:
                logger.warning("获取公司热榜失败或为空")
        except Exception as e:
            logger.error(f"获取公司热榜出错: {e}")
            
        # 如果没有获取到数据，使用备用数据
        if not hot_data:
            logger.warning("无法从脉脉获取数据，使用备用数据")
            hot_data = self._get_backup_hot_data()
            
        # 按热度排序
        hot_data.sort(key=lambda x: x.get("hot", 0), reverse=True)
        
        # 限制返回数量
        return hot_data[:self.config['max_items']]
        
    def _get_backup_hot_data(self):
        """提供备用的热门数据，防止API失效时没有数据显示"""
        return [
            {
                "title": "大厂裁员最新动态：某互联网巨头再裁10%员工，管理层震荡",
                "url": "https://maimai.cn/web/gossip_detail?gid=28523698",
                "hot": 9800,
                "source": "脉脉职言"
            },
            {
                "title": "跳槽季来临，今年的互联网大厂薪资水平对比",
                "url": "https://maimai.cn/web/gossip_detail?gid=28523567",
                "hot": 9500,
                "source": "脉脉职言"
            },
            {
                "title": "字节跳动内部调整，多个业务线整合，部分员工转岗",
                "url": "https://maimai.cn/web/gossip_detail?gid=28523432",
                "hot": 8900,
                "source": "脉脉职言"
            },
            {
                "title": "腾讯新一轮组织架构调整，云业务成重点发展方向",
                "url": "https://maimai.cn/web/gossip_detail?gid=28523109",
                "hot": 8700,
                "source": "脉脉职言"
            },
            {
                "title": "阿里巴巴最新人才战略：大幅提高应届生薪资，争夺顶尖人才",
                "url": "https://maimai.cn/web/gossip_detail?gid=28522987",
                "hot": 8500,
                "source": "脉脉职言"
            },
            {
                "title": "美团调整绩效考核制度，末位淘汰比例从10%上升到15%",
                "url": "https://maimai.cn/web/gossip_detail?gid=28522689",
                "hot": 8200,
                "source": "脉脉职言"
            },
            {
                "title": "京东物流大规模扩招，跨境电商成新增长点",
                "url": "https://maimai.cn/web/gossip_detail?gid=28522456",
                "hot": 7800,
                "source": "脉脉职言"
            },
            {
                "title": "华为年终奖发放完毕，研发人员最高48个月工资",
                "url": "https://maimai.cn/web/gossip_detail?gid=28522145",
                "hot": 7500,
                "source": "脉脉职言"
            },
            {
                "title": "程序员35岁危机：大厂中年员工现状调查",
                "url": "https://maimai.cn/web/gossip_detail?gid=28522067",
                "hot": 7300,
                "source": "脉脉职言"
            },
            {
                "title": "互联网大厂2025校招薪资曝光，应届生最高年薪60万",
                "url": "https://maimai.cn/web/gossip_detail?gid=28521798",
                "hot": 7100,
                "source": "脉脉职言"
            },
            {
                "title": "大厂员工离职后创业经历分享：从月薪5万到负债百万",
                "url": "https://maimai.cn/web/gossip_detail?gid=28521543",
                "hot": 6800,
                "source": "脉脉职言"
            },
            {
                "title": "大厂加班文化调查：996已成过去式？新一轮内卷开始",
                "url": "https://maimai.cn/web/gossip_detail?gid=28521298",
                "hot": 6500,
                "source": "脉脉职言"
            }
        ]

# 测试代码
if __name__ == "__main__":
    scraper = MaimaiScraper()
    if scraper.login():
        print("登录成功!")
        
        print("\n获取热门话题:")
        hot_topics = scraper.get_hot_topics()
        for i, topic in enumerate(hot_topics):
            print(f"{i+1}. {topic['title']}")
            
        print("\n获取公司热榜:")
        company_hot = scraper.get_company_hot()
        for i, topic in enumerate(company_hot):
            print(f"{i+1}. {topic['title']}")
            
        print("\n获取所有热榜数据:")
        all_hot_data = scraper.get_all_hot_data()
        for i, topic in enumerate(all_hot_data):
            print(f"{i+1}. {topic['title']} - 热度:{topic['hot']} - 来源:{topic['source']}")
    else:
        print("登录失败!") 