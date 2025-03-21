import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.agents import UserProxyAgent

model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        base_url="https://api.deepbricks.ai/v1/",
        api_key="sk-m3Hc5Ma8eQwfhDyzErikHmAqx8ZxculLqB0L7tIK3RQ3O6e0")

async def singleAI():
   
    
    assistant = AssistantAgent(
        name="助手1",
        model_client=model_client,
        system_message="你是一个文案写作高手，可以编写很多热点文案",
    )

    assistant.on_messages_stream([TextMessage(content="你好，请写一个关于秋天的三行诗", source="user")],)

    # response = await assistant.on_messages(
    #     messages=[TextMessage(content="你好，请写一个关于秋天的三行诗", source="user")],
    #     cancellation_token=CancellationToken()
    # )
    # print(response.chat_message.content)

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
    await Console(team.run_stream(task="写一个吸引人的热点话题，字数在100字内"))
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

asyncio.run(HumenInLoop())
# asyncio.run(singleAI())
# asyncio.run(MultAITeam())