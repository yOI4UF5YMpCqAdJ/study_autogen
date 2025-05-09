from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
import asyncio

# class Person():
#     def __init__(self,**info):
#         self.name = info.pName
#         self.age = info.pAge
#     def __str__(self):
#         return f"Person(name='{self.name}', age={self.age}, phone={self.phone})"
#     name:str
#     age:int
#     phone:list[str] = []


# def test():
#     info = {"pName":"w","pAge":20}
#     p = Person(**info)
#     # p = Person(pName='w',pAge=18)
#     p2 =  Person(pName='s',pAge=33)
#     p2.phone.append("11")

#     print(p)

async def main()->None:
    agent = AssistantAgent(
        name="crawlerAgent",
        model_client= OpenAIChatCompletionClient(
            base_url= "https://api.deerapi.com/v1",
            model="gpt-4o-mini",
            api_key="sk-oPvYSEW08UyS2z2MTspvual45dCLH9BvnNnPZ24OQ0woBzm2",
            
        ),
        tools=[],
        system_message="你是一个网络爬虫,需要根据任务需求，到网络中寻找爬取数据"
    )

    termination = TextMentionTermination("exit")

    response = await agent.on_messages([TextMessage(content="你好，你可以干嘛？",source="user")],cancellation_token=CancellationToken())

    print(response)

if __name__ == '__main__':
    # test()
    asyncio.run(main())



