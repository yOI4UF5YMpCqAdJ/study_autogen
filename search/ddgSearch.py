import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

def search_duckduckgo(query, num_results=10):
    """
    使用DuckDuckGo搜索引擎搜索关键词并返回指定数量的结果
    
    参数:
        query (str): 要搜索的关键词
        num_results (int): 需要返回的结果数量
        
    返回:
        list: 包含(标题, URL, 简短描述)的搜索结果列表
    """
    # 对查询进行URL编码
    encoded_query = urllib.parse.quote(query)
    base_url = "https://html.duckduckgo.com/html/"
    
    # 使用不同的User-Agent以避免被阻止
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    ]
    
    search_results = []
    page = 0
    s = requests.Session()
    
    # 继续获取结果，直到达到要求的数量
    while len(search_results) < num_results:
        # 构建搜索URL，DuckDuckGo使用's'参数进行分页
        params = {
            'q': query
        }
        
        if page > 0:
            params['s'] = page * 30  # DuckDuckGo每页显示约30个结果
            params['dc'] = page * 30 + 1
            params['v'] = 'l'
            params['o'] = 'json'
            params['api'] = 'd'
        
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://duckduckgo.com/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        try:
            # 发送搜索请求
            response = s.get(base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # DuckDuckGo的HTML搜索结果通常在类为result的div中
                results = soup.find_all('div', class_='result')
                
                # 如果没有找到结果，退出循环
                if not results:
                    print(f"第 {page+1} 页没有找到结果，停止搜索")
                    break
                
                print(f"第 {page+1} 页找到 {len(results)} 个结果")
                
                for result in results:
                    # 提取标题和URL
                    title_element = result.find('a', class_='result__a')
                    if not title_element:
                        continue
                        
                    title = title_element.text.strip()
                    
                    # 获取URL并清理
                    url = title_element.get('href')
                    if not url:
                        continue
                        
                    # DuckDuckGo的URL需要清理
                    if url.startswith('/'):
                        parsed_url = urllib.parse.urlparse(url)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        
                        if 'uddg' in query_params:
                            url = query_params['uddg'][0]
                        elif 'redirect' in query_params:
                            url = query_params['redirect'][0]
                        else:
                            # 尝试其他可能的参数
                            for param in query_params:
                                if query_params[param] and query_params[param][0].startswith('http'):
                                    url = query_params[param][0]
                                    break
                    
                    # 提取描述
                    desc_element = result.find('a', class_='result__snippet')
                    description = desc_element.text.strip() if desc_element else "无描述"
                    
                    # 添加结果
                    search_results.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })
                    
                    # 如果已经有足够的结果，退出循环
                    if len(search_results) >= num_results:
                        break
                
                # 查找"更多结果"按钮
                next_form = soup.find('form', {'action': '/html/', 'class': 'nav-form'})
                
                # 如果没有下一页或者没有更多结果可获取，退出循环
                if not next_form:
                    print("没有更多页面，停止搜索")
                    break
                
                # 增加页码
                page += 1
                
                # 添加延迟避免被封
                time.sleep(random.uniform(2, 3))
            else:
                print(f"DuckDuckGo请求失败，状态码: {response.status_code}")
                break
                
        except Exception as e:
            print(f"DuckDuckGo搜索过程中发生错误: {e}")
            break
    
    print(f"共获取到 {len(search_results)} 个结果")
    return search_results[:num_results]

def extract_duckduckgo_params(html):
    """从DuckDuckGo响应中提取下一页参数"""
    soup = BeautifulSoup(html, 'html.parser')
    next_form = soup.find('form', {'class': 'nav-form'})
    
    if not next_form:
        return None
    
    params = {}
    inputs = next_form.find_all('input')
    
    for input_tag in inputs:
        if 'name' in input_tag.attrs and 'value' in input_tag.attrs:
            params[input_tag['name']] = input_tag['value']
    
    return params

def get_webpage_details(url):
    """
    访问网页获取更多详细信息
    
    参数:
        url (str): 网页URL
        
    返回:
        dict: 包含标题和描述的字典
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.title.text.strip() if soup.title else "无标题"
            
            # 提取meta描述
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'].strip() if meta_desc and 'content' in meta_desc.attrs else ""
            
            # 如果没有meta描述，尝试获取页面的第一段文本
            if not description:
                first_p = soup.find('p')
                description = first_p.text.strip() if first_p else "无描述"
            
            return {
                "title": title,
                "description": description
            }
            
    except Exception as e:
        print(f"获取页面详情时出错 ({url}): {e}")
    
    # 如果出错，返回空值
    return {"title": "", "description": ""}

def search_keywords(query, num_results=10, get_details=False):
    """
    搜索关键词并返回结果，可选择是否获取更详细的网页信息
    
    参数:
        query (str): 要搜索的关键词
        num_results (int): 需要返回的结果数量
        get_details (bool): 是否获取更详细的网页信息
        
    返回:
        list: 搜索结果列表
    """
    print(f"正在搜索关键词 '{query}'...")
    print(f"尝试获取 {num_results} 个结果...")
    
    # 获取DuckDuckGo搜索结果
    results = search_duckduckgo(query, num_results)
    
    if get_details and results:
        print("正在获取更详细的网页信息...")
        
        for i, result in enumerate(results):
            print(f"处理结果 {i+1}/{len(results)}: {result['url']}")
            
            # 如果标题或描述不完整，尝试直接访问网页获取更多信息
            if not result['description'] or result['description'] == "无描述":
                details = get_webpage_details(result['url'])
                
                # 更新标题和描述
                if details['title']:
                    result['title'] = details['title']
                    
                if details['description']:
                    result['description'] = details['description']
            
            # 添加延迟，避免请求过快
            time.sleep(random.uniform(1, 2))
    
    return results

def save_results_to_file(results, filename="search_results.txt"):
    """将搜索结果保存到文本文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"找到 {len(results)} 个搜索结果:\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. {result['title']}\n")
            f.write(f"   URL: {result['url']}\n")
            f.write(f"   描述: {result['description']}\n\n")
    
    print(f"搜索结果已保存到 '{filename}'")

# 主程序
if __name__ == "__main__":
    keyword = input("请输入要搜索的关键词: ")
    num = int(input("请输入需要的结果数量: "))
    details = input("是否获取更详细的网页信息? (y/n): ").lower() == 'y'
    
    results = search_keywords(keyword, num, details)
    
    if results:
        print(f"\n找到 {len(results)} 个结果:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            
            # 如果描述太长，进行截断显示
            description = result['description']
            if len(description) > 150:
                print(f"   描述: {description[:150]}...")
            else:
                print(f"   描述: {description}")
                
            print()
            
        # 询问是否保存结果
        save_option = input("是否将结果保存到文件? (y/n): ").lower()
        if save_option == 'y':
            filename = input("请输入文件名 (默认为search_results.txt): ") or "search_results.txt"
            save_results_to_file(results, filename)
    else:
        print("未找到任何结果，请尝试不同的关键词或检查网络连接。") 