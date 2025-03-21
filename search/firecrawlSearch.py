from firecrawl import FirecrawlApp
import requests
import json


#  "User-Agent": "PostmanRuntime/7.43.2",
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Connection": "keep-alive"





# 请求头和请求体
headers = {"Content-Type": "application/json"}
endPoint = "http://localhost:3002"
def scrape(url):
    # API端点
    endPointUrl = "http://localhost:3002/v1/scrape"

 

    payload = {
        "url":url,
        "formats": ["markdown"]
    }
    response = requests.post(endPointUrl, headers=headers, json=payload)

    if response.status_code == 200:
      data = response.json()
      
      # 检查响应是否成功
      if data.get("success"):
          # 获取响应数据
          result = data.get("data", {})
          
          # 打印markdown内容（只显示前100个字符）
          markdown = result.get("markdown", "")
          print("Markdown内容:", markdown[:100] + "..." if markdown else "无")
          
          # 打印HTML内容（只显示前100个字符）
          html = result.get("html", "")
          print("HTML内容:", html[:100] + "..." if html else "无")
          
          # 打印元数据
          metadata = result.get("metadata", {})
          print("元数据:", metadata)
      else:
          print("请求失败:", data.get("error", "未知错误"))
    else:
        print(f"HTTP错误: {response.status_code}")
        print(response.text)

def search(query):
     searchPayLoad = {
        "query": query,
        "limit": 20,
        "lang": "CN",
        "country": "CN",
        "location": "CN",
        "timeout": 60000,
        "scrapeOptions": {}
    }
     url = "http://localhost:3002/v1/search"
     response = requests.post(url, headers=headers, json=searchPayLoad)
     if response.status_code == 200:
      data = response.json()
      
      # 检查响应是否成功
      if data.get("success"):
          # 获取响应数据
          result = data.get("data", {})
          print(result)

    
if __name__ == "__main__":
     search()
    # scrape()
 

