import requests
import json

def google_search(query, api_key, cx, num=10):
    """
    使用Google Custom Search API进行搜索
    
    参数:
    query (str): 搜索关键词
    api_key (str): Google API密钥
    cx (str): 自定义搜索引擎ID
    num (int): 返回结果数量（最大为10，如需更多需分页获取）
    
    返回:
    list: 搜索结果列表
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    # 请求参数
    params = {
        'q': query,       # 搜索查询
        'key': api_key,   # API密钥
        'cx': cx,         # 搜索引擎ID
        'num': num        # 结果数量
    }
    
    # 发送请求
    response = requests.get(base_url, params=params)
    
    # 检查请求是否成功
    if response.status_code != 200:
        return f"API请求失败，状态码: {response.status_code}，错误信息: {response.text}"
    
    # 解析返回结果
    results = response.json()
    
    # 处理结果
    search_results = []
    if 'items' in results:
        for item in results['items']:
            search_results.append({
                'title': item.get('title', '无标题'),
                'url': item.get('link', '无链接'),
                'description': item.get('snippet', '无描述')
            })
    
    return search_results

def google_search_with_pagination(query, api_key, cx, total_results=30):
    """
    使用分页获取更多搜索结果
    """
    all_results = []
    # 每页最多10个结果
    results_per_page = 10
    # 计算需要的页数
    num_pages = (total_results + results_per_page - 1) // results_per_page
    
    for page in range(num_pages):
        # 起始索引 (0, 10, 20, ...)
        start_index = page * results_per_page + 1
        
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': api_key,
            'cx': cx,
            'num': min(results_per_page, total_results - len(all_results)),
            'start': start_index
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            print(f"页面 {page+1} 请求失败: {response.text}")
            continue
        
        results = response.json()
        
        if 'items' in results:
            for item in results['items']:
                all_results.append({
                    'title': item.get('title', '无标题'),
                    'url': item.get('link', '无链接'),
                    'description': item.get('snippet', '无描述')
                })
        
        # 避免API限制，添加短暂延迟
        import time
        time.sleep(1)
        
        # 如果已经获取了足够的结果，提前结束
        if len(all_results) >= total_results:
            break
    
    return all_results[:total_results]

# 使用示例
if __name__ == "__main__":
    # 填入你自己的API密钥和搜索引擎ID
    API_KEY = "AIzaSyCX4lRUAgnN9hKOknKhJL9E_2Zk5QMvwJk"
    CX = "a0b2ec66fa6d7405d"
    
    query = input("请输入要搜索的关键词: ")
    num_results = int(input("请输入需要的结果数量 (最大10): "))
    
    results = google_search(query, API_KEY, CX, num_results)
    
    if isinstance(results, str):
        print(f"错误: {results}")
    else:
        print(f"\n找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   描述: {result['description']}")
            print()