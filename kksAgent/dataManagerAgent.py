import os
import sys
import dotenv
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_agentchat.ui import Console
from pathlib import Path
import pandas as pd
from cachetools import cached, LRUCache

from tools.weibo import weibo
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from newsData.newsApi import news_api
from kksAgent.tools.kksFileUtil import kks_saveFile

dotenv.load_dotenv()
deerApiKey = os.environ.get("deerApiKey")
ai_model = os.environ.get("ai_model")
ai_baseUrl = os.environ.get("ai_baseUrl")

class dataManagerAgent:
    def __init__(self):
        self.openai_model_client = OpenAIChatCompletionClient(
            model=ai_model,
            base_url=ai_baseUrl,
            api_key = deerApiKey
        )
        self.agent =  AssistantAgent(
            name="dataManager",
            
            model_client= self.openai_model_client,
            system_message="""
            你是一个数据处理和文案生成专家。按照以下步骤完成任务：
            1. 使用search_news工具获取热门新闻url
            2. 对每条新闻url,使用getContentFromPage工具获取详细内容
           
            返回格式要求：
            - 首先返回处理步骤的说明
            - 最后返回完整的HTML代码块
            """,
            tools=[self.search_news,self.getContentFromPage]
       )
        
    @cached(cache=LRUCache(maxsize=32))
    def search_news(self) -> pd.DataFrame:
        '''搜索文章'''
        ids = news_api.get_all_source_ids()
        result = pd.DataFrame()
        for id in ids:
            news_data = news_api.fetch_news_by_id(id)
            if news_data is None or news_data.get("status") != "success":
                continue
            # print(f"获取资源:{id}")
            pd_news = pd.DataFrame(news_data.get("items",[]))
            
            result = pd.concat([result,pd_news])

        return result
    
    def getContentFromPage(self,url:str)->str:
        # 
        page = weibo.gotoUrl(url)
        
      
        # weibo.login_with_storage_state(True)
        # weibo.end() '''获取文章内容'''
        return page.content()
        
        

async def main():    

    dmAgent = dataManagerAgent()
    # result = dmAgent.search_news_urls()
    
    stream = dmAgent.agent.run_stream(task="编写一篇500字的图文文案，生成一个微信公众号草稿的html")
    await Console(stream) 

 
def test():
    dmAgent = dataManagerAgent()
    dfData = dmAgent.search_news().head(5)
    for row in dfData.itertuples():
        page = weibo.gotoUrl(row.url)
        allContent = page.locator('div[action-type="feed_list_item"]').all()
        result = []
        for c in allContent:
            result.append(c.inner_html())
            


        content = ''.join(result)
        print(content)
        saveFile = Path(__file__).parent.parent/f'weibo/article/{row.title}.txt'
        kks_saveFile(saveFile,content)

        


if __name__ == "__main__":
    
    # import nest_asyncio
    # nest_asyncio.apply()

   
    # asyncio.run(main())

    test()
