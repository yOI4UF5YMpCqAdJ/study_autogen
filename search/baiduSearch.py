import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import time

def baidu_search(keyword, num_results=10):
    """
    使用百度搜索指定关键词并返回指定数量的结果集合
    
    参数:
    keyword (str): 要搜索的关键词
    num_results (int): 需要返回的结果数量
    
    返回:
    list: 包含(标题, URL, 简短描述)的搜索结果列表
    """
    # 对关键词进行URL编码
    encoded_query = urllib.parse.quote(keyword)
    
    # 构建百度搜索URL
    search_url = f"https://www.baidu.com/s?wd={encoded_query}&rn={num_results}"
    
    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }
    
    # 发送HTTP请求
    response = requests.get(search_url, headers=headers)
    
    # 检查请求是否成功
    if response.status_code != 200:
        return f"请求失败，状态码: {response.status_code}"
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取搜索结果
    search_results = []
    
    # 百度搜索结果通常在class为"result"的div中
    result_blocks = soup.select('div.result, div.result-op')
    
    for block in result_blocks:
        if len(search_results) >= num_results:
            break
            
        # 尝试提取标题和URL
        title_element = block.select_one('h3 a')
        
        if title_element:
            title = title_element.get_text().strip()
            link = title_element.get('href')  # 这是百度的重定向链接
            
            # 尝试提取描述
            desc_element = block.select_one('div.c-abstract, div.c-span-last')
            description = desc_element.get_text().strip() if desc_element else "无描述"
            
            search_results.append({
                "title": title,
                "url": link,  # 注意：这是百度的跳转链接，非最终URL
                "description": description
            })
    
    # 对于每个搜索结果，获取真实URL
    for result in search_results:
        try:
            # 跟随重定向链接获取真实URL
            redirect_response = requests.head(result['url'], headers=headers, allow_redirects=True)
            result['url'] = redirect_response.url
        except Exception as e:
            # 如果获取真实URL失败，保留原始URL
            print(f"获取真实URL失败: {e}")
            pass
    
    return search_results

def baidu_search_api(keyword, api_key, num_results=10):
    """
    使用百度搜索API进行搜索
    注意：这需要申请百度开发者账号和API密钥
    
    参数:
    keyword (str): 搜索关键词
    api_key (str): 百度API密钥
    num_results (int): 返回结果数量
    
    返回:
    list: 搜索结果列表
    """
    # 百度WebAPI接口地址
    api_url = "http://api.baidu.com/json/search/web"
    
    # 请求参数
    params = {
        'query': keyword,  # 搜索关键词
        'apikey': api_key, # API密钥
        'results': num_results  # 结果数量
    }
    
    # 发送请求
    response = requests.get(api_url, params=params)
    
    # 检查请求是否成功
    if response.status_code != 200:
        return f"API请求失败，状态码: {response.status_code}，错误信息: {response.text}"
    
    # 解析返回结果
    results = response.json()
    
    # 处理结果
    search_results = []
    for item in results.get('results', []):
        search_results.append({
            'title': item.get('title', '无标题'),
            'url': item.get('url', '无链接'),
            'description': item.get('abstract', '无描述')
        })
    
    return search_results

# 示例使用
if __name__ == "__main__":
    keyword = input("请输入要搜索的关键词: ")
    num = int(input("请输入需要的结果数量: "))
    
    print(f"\n正在使用百度搜索关键词 '{keyword}'，获取 {num} 个结果...")
    
    try:
        # 使用网页抓取方式
        results = baidu_search(keyword, num)
        
        if isinstance(results, str):  # 如果返回错误信息
            print(f"搜索失败: {results}")
            exit(1)
        
        print(f"\n找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   描述: {result['description'][:150]}...")
            print()
            
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")