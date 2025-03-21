from firecrawl import FirecrawlApp
import requests
import json

api_url="http://localhost:3002"
def scrapeByApi(targetUrl):
    app = FirecrawlApp(api_url=api_url)
  
    try:
        return app.scrape_url(
            url=targetUrl, 
            params={
                'formats': ['markdown'],
                'timeout': 30000  # 30秒超时
            }
        )
    except Exception as e:
        print(f"抓取失败: {str(e)}")
        return None

def searchByApi(keyWord):
    app = FirecrawlApp(api_url=api_url)

    parms = {
      
      "limit": 20,
      "lang": "CN",
      "country": "CN",
      "location": "CN",
      "timeout": 60000,
      "scrapeOptions": {},
      
  }
  
    return app.search(
      query=keyWord,
      params=parms
    )

if __name__ == "__main__":
    #  searchByApi("赢在一起")
   data =  scrapeByApi("https://www.ogilvy.com/cn/work/yongbaocike-rangwomenyingzaiyiqi")
   print(data)
