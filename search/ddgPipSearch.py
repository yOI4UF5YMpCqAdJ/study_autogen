from duckduckgo_search import DDGS

def custom_search(keyword, max_results=10, search_type="text", region="wt-wt", 
                  safesearch="moderate", timelimit=None):
    """
    使用 DuckDuckGo 搜索引擎进行自定义搜索
    
    参数:
        keyword (str): 搜索关键词
        max_results (int): 要返回的最大结果数量
        search_type (str): 搜索类型，可选值: "text", "images", "news", "videos"
        region (str): 搜索区域，例如 "cn" 代表中国, "wt-wt" 代表全球
        safesearch (str): 安全搜索级别，可选值: "on", "moderate", "off"
        timelimit (str): 时间限制，可选值: "d" (天), "w" (周), "m" (月), "y" (年)
    
    返回:
        list: 搜索结果列表
    """
    # 创建 DDGS 实例
    ddgs = DDGS()
    
    # 根据搜索类型调用相应的方法
    if search_type == "text":
        results = ddgs.text(
            keyword, 
            region=region, 
            safesearch=safesearch, 
            timelimit=timelimit, 
            max_results=max_results
        )
    elif search_type == "images":
        results = ddgs.images(
            keyword, 
            region=region, 
            safesearch=safesearch, 
            timelimit=timelimit, 
            max_results=max_results
        )
    elif search_type == "news":
        results = ddgs.news(
            keyword, 
            region=region, 
            safesearch=safesearch, 
            timelimit=timelimit, 
            max_results=max_results
        )
    elif search_type == "videos":
        results = ddgs.videos(
            keyword, 
            region=region, 
            safesearch=safesearch, 
            timelimit=timelimit, 
            max_results=max_results
        )
    else:
        raise ValueError("不支持的搜索类型。请使用 'text', 'images', 'news' 或 'videos'")
    
    # 将生成器转换为列表返回
    return list(results)

# 示例使用方法
if __name__ == "__main__":
    # keyword = input("请输入要搜索的关键词: ")
    # num = int(input("请输入需要的结果数量: "))
    keyword = "赢在一起"
    num = 100
    region = "wt-wt"
    # 搜索文本
    text_results = custom_search(keyword, max_results=num,region=region)
    print("文本搜索结果:")
    for i, result in enumerate(text_results, 1):
        print(f"{i}. 标题: {result['title']}")
        print(f"   链接: {result['href']}")
        print(f"   摘要: {result['body']}")
        print("---")
    
    # # 搜索图片
    # image_results = custom_search("猫咪", max_results=3, search_type="images")
    # print("\n图片搜索结果:")
    # for i, result in enumerate(image_results, 1):
    #     print(f"{i}. 标题: {result['title']}")
    #     print(f"   图片链接: {result['image']}")
    #     print("---")
    
    # # 搜索新闻
    # news_results = custom_search("科技新闻", max_results=3, search_type="news", timelimit="w")
    # print("\n新闻搜索结果 (最近一周):")
    # for i, result in enumerate(news_results, 1):
    #     print(f"{i}. 标题: {result['title']}")
    #     print(f"   链接: {result['url']}")
    #     print(f"   日期: {result.get('date', '未知')}")
    #     print("---")