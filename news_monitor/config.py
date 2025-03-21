import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firecrawl API 配置
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 邮件配置
SMTP_SERVER = "smtp.gmail.com"  # 替换为你的SMTP服务器
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# 新闻监控配置
CHECK_INTERVAL = 3600  # 检查间隔（秒）
MAX_NEWS_PER_BATCH = 10  # 每次获取的新闻数量
