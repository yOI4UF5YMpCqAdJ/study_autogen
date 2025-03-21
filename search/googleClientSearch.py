from googleapiclient.discovery import build

# 设置 API 密钥和搜索引擎 ID
api_key = "AIzaSyCX4lRUAgnN9hKOknKhJL9E_2Zk5QMvwJk"  # 替换为你获得的 API 密钥
cse_id = "a0b2ec66fa6d7405d"    # 替换为你创建的自定义搜索引擎 ID

# 构建 Google 搜索服务
service = build("customsearch", "v1", developerKey=api_key)

def google_search(query, num_results=10):
    # 执行搜索请求

    res = service.cse().list(q=query, cx=cse_id, num=num_results).execute()
    search_results = []

    # 获取搜索结果
    if "items" in res:
        for item in res["items"]:
            search_results.append({
                "title": item["title"],
                "link": item["link"]
            })

    return search_results

# 示例：查询“Python programming”
query = "Python programming"
results = google_search(query, num_results=5)
for idx, result in enumerate(results):
    print(f"{idx+1}: {result['title']} - {result['link']}")