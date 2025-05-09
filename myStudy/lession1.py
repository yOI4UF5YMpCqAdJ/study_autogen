import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import UserProxyAgent

import os
import dotenv
dotenv.load_dotenv()
deerApiKey = os.environ.get("deerApiKey")
ai_model = os.environ.get("ai_model")
ai_baseUrl = os.environ.get("ai_baseUrl")

model_client = OpenAIChatCompletionClient(
        model=ai_model,
        base_url=ai_baseUrl,
        api_key=deerApiKey)

def searchAI():
    pass

async def singleAI():
   
    assistant = AssistantAgent(
        name="助手1",
        model_client=model_client,
        system_message="你是一个文案写作高手，可以编写很多热点文案",
    )

    await Console(assistant.run_stream(task="通过新闻工具，帮我获取10条当前最热的信息，然后获取对应的网页内容，总结归纳后编写一篇500字的图文文案，生成一个微信公众号草稿的html"))


async def MultAITeam():
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message="你是一个文案写作高手，可以编写很多热点文案",
    )

    critic = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message="你是一个文案评论员,当你觉得文章写的符合要求并且具有较强吸引力时,回答'APPROVE'"
    )

    termination = TextMentionTermination("APPROVE")
    team = RoundRobinGroupChat([writer,critic],termination,10)
    await Console(team.run_stream(task="帮我获取10条当前最热的信息，然后获取对应的网页内容，总结归纳后编写一篇500字的文案，配上上当生成一个微信公众号草稿的html"))
    # team.run()
    #1

'''人机交互'''
async def HumenInLoop():
    assistant = AssistantAgent("assistant", model_client=model_client)
    userProxy  = UserProxyAgent("userProxy",input_func=input)

    termination = TextMentionTermination("APPROVE")

    team = RoundRobinGroupChat([assistant,userProxy],termination_condition=termination)
    await Console(team.run_stream(task="写一个吸引人的热点话题，字数在100字内"))

'''selectGroupChat'''
async def selectGroupChat(): 
    pass

asyncio.run(singleAI())
