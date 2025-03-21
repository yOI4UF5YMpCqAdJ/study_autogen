import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from datetime import datetime
import os
from dotenv import load_dotenv
from utils.news_processor import NewsProcessor
from utils.email_sender import EmailSender

# Load environment variables
load_dotenv()

# 配置 OpenAI 客户端
model_client = OpenAIChatCompletionClient(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.deepbricks.ai/v1/"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

# 初始化工具类
news_processor = NewsProcessor()
email_sender = EmailSender()

# 创建团队成员
news_collector = AssistantAgent(
    name="news_collector",
    description="""新闻收集专家，负责：
    1. 调用NewsProcessor获取最新热点新闻
    2. 确保新闻数据的质量和完整性
    3. 将新闻内容传递给编辑处理
    擅长：收集和整理新闻数据""",
    model_client=model_client,
    system_message="""你是新闻收集专家，使用NewsProcessor获取最新热点新闻。
执行任务时，请使用以下代码：
```python
news_report = news_processor.process_news(["热点", "新闻"])
print(news_report)  # 输出新闻报告供其他agent使用
```
注意：确保收集的新闻质量和完整性。""",
)

news_editor = AssistantAgent(
    name="news_editor",
    description="""新闻编辑，负责：
    1. 分析和整理新闻内容
    2. 生成简洁明了的新闻摘要
    3. 按重要性排序
    擅长：新闻编辑和内容优化""",
    model_client=model_client,
    system_message="""你是新闻编辑，负责审核和优化新闻报告。
收到新闻报告后：
1. 检查内容的完整性和准确性
2. 优化内容结构和表述
3. 必要时补充相关信息
4. 完成编辑后输出'APPROVE'""",
)

email_agent = AssistantAgent(
    name="email_agent",
    description="""邮件发送专家，负责：
    1. 接收新闻报告并发送邮件
    2. 确保邮件发送成功
    3. 处理可能的错误
    擅长：邮件发送和错误处理""",
    model_client=model_client,
    system_message="""你是邮件发送专家，负责发送新闻报告。
执行任务时，请使用以下代码：
```python
success = email_sender.send_report(news_report)
if success:
    print("邮件发送成功")
    print("TERMINATE")
else:
    print("邮件发送失败")
```""",
)

async def monitor_news():
    """定期监控新闻的主函数"""
    # 获取配置的检查间隔时间
    check_interval = int(os.getenv("CHECK_INTERVAL", 3600))
    
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{current_time}] 开始新一轮新闻检查...")
        
        # 设置终止条件
        termination = TextMentionTermination("TERMINATE")
        
        # 创建智能选择器团队
        team = SelectorGroupChat(
            agents=[news_collector, news_editor, email_agent],
            selector_persona="""你是一个新闻处理团队的协调者。根据每个agent的专长和当前任务阶段，
            选择最合适的agent来执行任务。
            
            工作流程：
            1. 新闻收集阶段：选择news_collector
            2. 内容编辑阶段：选择news_editor
            3. 邮件发送阶段：选择email_agent
            
            选择时考虑：
            - 任务的具体需求
            - agent的专长领域
            - 工作流程的顺序性
            """,
            condition=termination,
            max_rounds=10,
            model_client=model_client
        )
        
        # 启动团队工作
        await team.run_stream(
            task="""执行新闻监控任务：

第一阶段：新闻收集
- news_collector负责获取最新热点新闻
- 使用NewsProcessor的process_news方法
- 确保获取高质量的新闻数据

第二阶段：内容编辑
- news_editor负责处理新闻内容
- 优化格式和表述
- 完成后输出'APPROVE'

第三阶段：邮件发送
- email_agent负责发送新闻报告
- 使用EmailSender发送邮件
- 成功后输出'TERMINATE'

注意：请按照流程顺序执行，确保每个阶段的任务都完成后再进入下一阶段。"""
        )

        # 等待配置的时间间隔后再次执行
        await asyncio.sleep(check_interval)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_news())
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"\n程序出错: {str(e)}")
