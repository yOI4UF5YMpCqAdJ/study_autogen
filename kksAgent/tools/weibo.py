"""
使用Python版Playwright的Storage State功能保存微博登录状态
支持用户手动登录并保存状态
"""
import os
import json
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

toUrl = "https://s.weibo.com/weibo?q=%E6%9C%88%E8%96%AA%E4%B8%89%E5%8D%834%E5%B9%B4%E5%AD%98%E4%BA%8610%E4%B8%87%E5%9D%97"

class weiboManager:

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.storage_state_path = Path(__file__).parent.parent.parent / 'weibo/weibo_storage_state.json'
        self.browser = self.playwright.chromium.launch(headless=True)
        if os.path.exists(self.storage_state_path):
            print("找到已保存的登录状态，尝试加载...")
            # 创建一个新的浏览器上下文并加载保存的状态
            self.context = self.browser.new_context(storage_state=self.storage_state_path)
            print("成功加载保存的登录状态")
        else:
            print("未找到保存的登录状态，将需要登录")
            # 创建一个新的浏览器上下文
            self.context = self.browser.new_context()
        pass

    def end(self):
        self.browser.close()
        self.playwright.stop()

    def gotoUrl(self,toUrl):
         page = self.context.new_page()
         page.goto(toUrl)
         page.get_attribute
        
        
         page.wait_for_timeout(2000)
         return page

    def isLoginPage(self,page):
        return page.url.startswith("https://passport.weibo.com/")
    
    def login_with_storage_state(self,headless=True):
        """使用存储状态保存和恢复微博登录会话，支持用户手动登录"""
        # 存储状态的文件路径
        
        try:
            page = self.context.new_page()
            if page.url.startswith("https://passport.weibo.com/"):
                txtPhone = page.get_by_role("textbox", name="手机号")
                txtPhone.click()
                txtPhone.fill("19370659060")

                page.get_by_text("获取验证码").click()
                
                # 等待用户登录完成
                # wait_for_login_completion(page)
                page.wait_for_timeout(90*1000)   
                # 保存登录状态到文件
                print("正在保存登录状态...")
                self.context.storage_state(path=self.storage_state_path)
                print(f"登录状态已保存到 {self.storage_state_path}")

                if not page.url.startswith(toUrl):
                    page.goto(toUrl)
                    page.wait_for_timeout(2000)

        finally:
            pass
            
    
            

weibo = weiboManager()

def main():
    """主函数"""
    print("启动微博自动化脚本...")
    
    weibo.weibo_login_with_storage_state(False)

if __name__ == "__main__":
    main()
