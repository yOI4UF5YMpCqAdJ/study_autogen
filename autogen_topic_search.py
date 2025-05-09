import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from search.firecrawlApi import searchByApi
from search.ddgSearch import search_keywords
from collections import Counter
from datetime import datetime

# 配置模型客户端
# model_client = OpenAIChatCompletionClient(
#     base_url="https://api.deerapi.com/v1",
#     model="gpt-4o-mini",
#     api_key="sk-oPvYSEW08UyS2z2MTspvual45dCLH9BvnNnPZ24OQ0woBzm2"
# )

class TopicSearchManager:
    @staticmethod
    async def search_and_analyze(keyword):
        try:
            print(f"\n尝试使用Firecrawl搜索关键词 '{keyword}' 的热门话题...")
            results = searchByApi(keyword)
            
            if not results:
                raise Exception("Firecrawl未返回结果")
            
            analyzed_results = TopicSearchManager._analyze_results(results, source="firecrawl")
            return TopicSearchManager._format_results(analyzed_results)
            
        except Exception as e:
            print(f"Firecrawl搜索失败 ({str(e)})，切换到DuckDuckGo搜索...")
            try:
                # 使用DuckDuckGo搜索作为备选
                results = search_keywords(keyword, num_results=20, get_details=True)
                if not results:
                    return "未找到相关结果"
                
                analyzed_results = TopicSearchManager._analyze_results(results, source="ddg")
                return TopicSearchManager._format_results(analyzed_results)
                
            except Exception as e2:
                return f"所有搜索尝试均失败: {str(e2)}"
    
    @staticmethod
    def _analyze_results(results, source="firecrawl"):
        # 统一结果格式
        unified_results = []
        
        if source == "firecrawl":
            if isinstance(results, dict) and 'results' in results:
                results = results['results']
            
            if not isinstance(results, list):
                return []
                
            for result in results:
                if isinstance(result, dict):
                    unified_results.append({
                        'title': result.get('title', ''),
                        'description': result.get('description', ''),
                        'url': result.get('url', ''),
                        'date': result.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    })
        
        elif source == "ddg":
            for result in results:
                unified_results.append({
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'url': result.get('url', ''),
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # 对统一格式的结果进行分析
        word_counter = Counter()
        analyzed_topics = []
        
        for result in unified_results:
            title = result['title']
            description = result['description']
            
            # 统计词频
            words = title.lower().split() + description.lower().split()
            word_counter.update(words)
            
            # 计算相关度分数
            topic = {
                'title': title,
                'description': description,
                'url': result['url'],
                'time': result['date'],
                'relevance_score': sum(word_counter[word.lower()] for word in words if len(word) > 1)
            }
            
            analyzed_topics.append(topic)
        
        analyzed_topics.sort(key=lambda x: x['relevance_score'], reverse=True)
        return analyzed_topics[:10]
    
    @staticmethod
    def _format_results(results):
        if not results:
            return "未找到热门话题。"
        
        output = "\n找到以下热门话题：\n"
        for i, topic in enumerate(results, 1):
            output += f"\n{i}. {topic['title']}"
            output += f"\n   描述: {topic['description']}"
            output += f"\n   链接: {topic['url']}"
            output += f"\n   时间: {topic['time']}"
            output += f"\n   热度分数: {topic['relevance_score']}\n"
        
        return output

async def topic_search_team(keyword):
    # 创建搜索分析师智能体
    analyst = AssistantAgent(
        name="analyst",
        model_client=model_client,
        system_message="""你是一个搜索分析专家，负责分析热门话题。你的任务是：
        1. 分析每个话题的重要性和相关性
        2. 对结果进行分类和总结
        3. 提供深入的见解和观点
        4. 当你认为分析很好时，回复'Approve'"""
    )
    
    # 创建评论智能体
    critic = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message="""你是一个评论专家，负责评价分析结果。你的任务是：
        1. 评估分析的质量和深度
        2. 提供建设性的反馈
        3. 确保分析全面且有见地
        4. 只有当你完全满意时才回复'Approve'"""
    )
    
    # 设置终止条件
    text_termination = TextMentionTermination("Approve")
    max_message_termination = MaxMessageTermination(10)
    termination = text_termination | max_message_termination
    
    # 创建团队
    team = RoundRobinGroupChat(
        participants=[analyst, critic],
        termination_condition=termination,
        max_turns=None
    )
    
    # 搜索并获取结果
    search_results = await TopicSearchManager.search_and_analyze(keyword)
    
    # 启动团队对话
    task = f"""
    我已经搜索到了关于"{keyword}"的热门话题，这是搜索结果：
    
    {search_results}
    
    请分析这些结果，提供你的见解。
    """
    
    stream = team.run_stream(task=task)
    await Console(stream)

async def search_hot_topics():
    """搜索当前最热门的话题"""
    try:
        print("\n开始搜索当前最热门话题...")
        try:
            # 先尝试使用firecrawl
            print("尝试使用Firecrawl搜索...")
            results = searchByApi("")
        except Exception as e:
            print(f"Firecrawl搜索失败: {str(e)}")
            print("切换到DuckDuckGo搜索...")
            # 使用多个关键词组合获取更全面的热门话题
            queries = [
                "今日热点新闻",
                "实时热搜",
                "今日头条热点",
                "社会热点话题"
            ]
            results = []
            for query in queries:
                print(f"搜索关键词: {query}")
                try:
                    query_results = search_keywords(query, num_results=10, get_details=True)
                    results.extend(query_results)
                except Exception as e2:
                    print(f"DuckDuckGo搜索 '{query}' 失败: {str(e2)}")
                    continue
        
        # 从结果中提取前10个热门话题
        top_topics = TopicSearchManager._analyze_results(results, source="firecrawl" if isinstance(results, dict) else "ddg")[:10]
        
        print("\n找到以下热门话题，开始深入分析每个话题...\n")
        detailed_results = {}
        
        for topic in top_topics:
            topic_title = topic['title']
            print(f"\n正在深入分析话题: {topic_title}")
            
            # 对每个话题进行深入搜索
            try:
                topic_results = searchByApi(topic_title)
                if not topic_results:
                    topic_results = search_keywords(topic_title, num_results=10, get_details=True)
                
                detailed_results[topic_title] = TopicSearchManager._analyze_results(
                    topic_results,
                    source="firecrawl" if isinstance(topic_results, dict) else "ddg"
                )[:10]
            except Exception as e:
                print(f"分析话题 '{topic_title}' 时出错: {str(e)}")
                detailed_results[topic_title] = []
        
        return top_topics, detailed_results
    except Exception as e:
        print(f"搜索热门话题时发生错误: {str(e)}")
        return [], {}

async def format_hot_topics_results(top_topics, detailed_results):
    """格式化热门话题和详细内容的结果"""
    output = "\n当前热门话题分析报告：\n"
    output += "=" * 50 + "\n"
    
    for i, topic in enumerate(top_topics, 1):
        output += f"\n{i}. 热门话题：{topic['title']}\n"
        output += f"   相关度：{topic['relevance_score']}\n"
        output += f"   话题描述：{topic['description']}\n"
        output += f"   来源链接：{topic['url']}\n"
        
        # 添加该话题的详细内容
        if topic['title'] in detailed_results and detailed_results[topic['title']]:
            output += "\n   相关内容：\n"
            for j, detail in enumerate(detailed_results[topic['title']], 1):
                output += f"\n   {j}) {detail['title']}\n"
                output += f"      描述：{detail['description']}\n"
                output += f"      链接：{detail['url']}\n"
        else:
            output += "\n   没有找到相关详细内容\n"
        
        output += "\n" + "-" * 40 + "\n"
    
    return output

async def main():
    keyword = input("请输入要搜索的关键词（直接回车将搜索当前最热门话题）: ").strip()
    
    if not keyword:
        # 搜索热门话题并深入分析
        top_topics, detailed_results = await search_hot_topics()
        if top_topics:
            formatted_results = await format_hot_topics_results(top_topics, detailed_results)
            # 创建任务进行分析
            task = f"""
            这是当前最热门的话题分析报告：
            
            {formatted_results}
            
            请分析这些话题，重点关注：
            1. 话题的重要性和影响力
            2. 话题之间的关联性
            3. 社会关注度和讨论热度
            4. 对未来发展的预测
            """
            await topic_search_team(task)
        else:
            print("未能获取到热门话题，请稍后重试。")
    else:
        # 搜索特定关键词
        await topic_search_team(keyword)

if __name__ == "__main__":
    asyncio.run(main())
