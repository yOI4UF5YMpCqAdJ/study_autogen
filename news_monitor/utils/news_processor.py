import os
from datetime import datetime
from firecrawl import FirecrawlApp
from ..config import MAX_NEWS_PER_BATCH

class NewsProcessor:
    def __init__(self):
        self.api_url = "http://localhost:3002"
        self.app = FirecrawlApp(api_url=self.api_url)
        
    def fetch_news(self, keywords=["热点", "新闻"]):
        """
        使用Firecrawl API获取最新新闻
        返回: list of dict, 每个dict包含新闻信息
        """
        try:
            all_news = []
            for keyword in keywords:
                params = {
                    "limit": MAX_NEWS_PER_BATCH,
                    "lang": "CN",
                    "country": "CN",
                    "location": "CN",
                    "timeout": 60000,
                    "scrapeOptions": {},
                }
                
                results = self.app.search(query=keyword, params=params)
                if results:
                    all_news.extend(results)
            
            # 对新闻进行去重和处理
            processed_news = []
            seen_urls = set()
            
            for news in all_news:
                if news.get('url') and news.get('url') not in seen_urls:
                    seen_urls.add(news.get('url'))
                    # 获取详细内容
                    try:
                        details = self.app.scrape_url(
                            url=news['url'],
                            params={
                                'formats': ['markdown'],
                                'timeout': 30000
                            }
                        )
                        
                        processed_news.append({
                            'title': news.get('title', '无标题'),
                            'url': news['url'],
                            'summary': details.get('text', '')[:500] + '...' if details and details.get('text') else news.get('description', '无描述'),
                            'published_time': news.get('published_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        })
                        
                        if len(processed_news) >= MAX_NEWS_PER_BATCH:
                            break
                            
                    except Exception as e:
                        print(f"获取新闻详情失败: {str(e)}")
                        continue
            
            return processed_news
            
        except Exception as e:
            error_msg = f"新闻获取失败: {str(e)}"
            print(error_msg)
            return []

    @staticmethod
    def format_news_report(news_items):
        """
        将新闻整理成格式化的报告
        参数:
            news_items: list of dict, 新闻列表
        返回:
            str, 格式化的新闻报告
        """
        if not news_items:
            return "当前时段没有新的热点新闻。"

        report = f"热点新闻摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 按发布时间排序
        sorted_news = sorted(
            news_items, 
            key=lambda x: datetime.strptime(x['published_time'], '%Y-%m-%d %H:%M:%S') if isinstance(x['published_time'], str) else x['published_time'],
            reverse=True
        )
        
        for i, news in enumerate(sorted_news[:MAX_NEWS_PER_BATCH], 1):
            report += f"{i}. {news['title']}\n"
            if news.get('summary'):
                report += f"   摘要：{news['summary']}\n"
            if news.get('url'):
                report += f"   源链接：{news['url']}\n"
            if news.get('published_time'):
                report += f"   发布时间：{news['published_time']}\n"
            report += "\n"
        
        return report

    def process_news(self, keywords=None):
        """
        获取并处理新闻的主函数
        参数:
            keywords: list, 搜索关键词列表
        返回:
            str, 格式化的新闻报告
        """
        if keywords is None:
            keywords = ["热点", "新闻"]
            
        try:
            news_items = self.fetch_news(keywords)
            return self.format_news_report(news_items)
        except Exception as e:
            error_msg = f"新闻处理出错：{str(e)}"
            print(error_msg)
            return error_msg
