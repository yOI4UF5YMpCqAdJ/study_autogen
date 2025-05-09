from search.firecrawlApi import searchByApi
from collections import Counter
from datetime import datetime
import json

class TopicAnalyzer:
    def __init__(self):
        self.results = []

    def analyze_topics(self, keyword):
        print(f"\n正在搜索关键词 '{keyword}' 的热门话题...")
        
        try:
            # 使用firecrawl API搜索
            search_results = searchByApi(keyword)
            
            if search_results:
                # 处理搜索结果
                self._process_results(search_results)
                return self._get_top_topics(10)
            else:
                print("未获取到搜索结果")
                return []
            
        except Exception as e:
            print(f"搜索过程中发生错误: {str(e)}")
            return []

    def _process_results(self, results):
        """处理搜索结果，计算热度分数"""
        self.results = []
        
        # 确保results是列表类型
        if not isinstance(results, list):
            if isinstance(results, dict) and 'results' in results:
                results = results['results']
            else:
                return

        # 使用Counter统计标题和描述中的关键词频率
        word_counter = Counter()
        
        for result in results:
            if isinstance(result, dict):
                # 统计标题和描述中的关键词
                title = result.get('title', '')
                description = result.get('description', '')
                
                words = title.lower().split() + description.lower().split()
                word_counter.update(words)
                
                # 创建话题对象
                topic = {
                    'title': title,
                    'description': description,
                    'url': result.get('url', ''),
                    'time': result.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    'relevance_score': 0  # 初始化热度分数
                }
                
                # 计算热度分数
                topic['relevance_score'] = sum(word_counter[word.lower()] for word in words if len(word) > 1)
                
                self.results.append(topic)
        
        # 根据热度分数排序
        self.results.sort(key=lambda x: x['relevance_score'], reverse=True)

    def _get_top_topics(self, limit=10):
        """返回前N个最热门的话题"""
        return self.results[:limit]

def main():
    # 获取用户输入
    keyword = input("请输入要搜索的关键词: ")
    
    # 创建分析器实例
    analyzer = TopicAnalyzer()
    
    # 执行搜索和分析
    top_topics = analyzer.analyze_topics(keyword)
    
    # 展示结果
    if top_topics:
        print("\n找到以下热门话题：")
        for i, topic in enumerate(top_topics, 1):
            print(f"\n{i}. {topic['title']}")
            print(f"   描述: {topic['description']}")
            print(f"   链接: {topic['url']}")
            print(f"   时间: {topic['time']}")
            print(f"   热度分数: {topic['relevance_score']}")
    else:
        print("\n未找到相关热门话题。")

if __name__ == "__main__":
    main()
