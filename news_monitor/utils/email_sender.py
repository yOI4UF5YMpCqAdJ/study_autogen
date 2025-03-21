import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from ..config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    RECIPIENT_EMAIL
)

class EmailSender:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.recipient = RECIPIENT_EMAIL
        
    def send_report(self, report_content):
        """
        使用126邮箱发送新闻报告
        参数:
            report_content: str, 新闻报告内容
        返回:
            bool, 发送是否成功
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = self.recipient
            msg['Subject'] = f"热点新闻摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            msg.attach(MIMEText(report_content, 'plain', 'utf-8'))
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 使用SSL连接
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 新闻报告邮件发送成功")
            return True

        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}")
            return False

    def test_connection(self):
        """
        测试126邮箱服务器连接
        返回:
            bool, 连接测试是否成功
        """
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
            print("邮件服务器连接测试成功")
            return True
        except Exception as e:
            print(f"邮件服务器连接测试失败: {str(e)}")
            return False
