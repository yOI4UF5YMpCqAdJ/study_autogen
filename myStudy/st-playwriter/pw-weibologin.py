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


def weibo_login_with_storage_state():
    """使用存储状态保存和恢复微博登录会话，支持用户手动登录"""
    
    # 存储状态的文件路径
    storage_state_path = Path(__file__).parent.parent.parent / 'weibo/weibo_storage_state.json'
   
    with sync_playwright() as p:
        browser_type = p.chromium
        # 启动浏览器
        browser = browser_type.launch(headless=True)

        # 检查是否存在已保存的状态文件
        if os.path.exists(storage_state_path):
            print("找到已保存的登录状态，尝试加载...")
            # 创建一个新的浏览器上下文并加载保存的状态
            context = browser.new_context(storage_state=storage_state_path)
            print("成功加载保存的登录状态")
        else:
            print("未找到保存的登录状态，将需要登录")
            # 创建一个新的浏览器上下文
            context = browser.new_context()
        
        # 创建一个新页面
        page = context.new_page()
        
        # 访问目标页面
        page.goto(toUrl)
        page.wait_for_timeout(2000)
       

        # 检查是否跳转到了登录页面
        if page.url.startswith("https://passport.weibo.com/"):
            print("\n============================================")
            print("检测到登录页面。请在浏览器中手动完成登录。")
            print("登录完成后，程序将自动保存登录状态。")
            print("============================================\n")
            
            # 等待用户登录完成
            # wait_for_login_completion(page)
            page.wait_for_timeout(60*1000)   
            # 保存登录状态到文件
            print("正在保存登录状态...")
            context.storage_state(path=storage_state_path)
            print(f"登录状态已保存到 {storage_state_path}")
        
        # 执行后续操作
        print("继续执行后续操作...")
        
        # 确保页面已经加载到目标页
        if not page.url.startswith(toUrl):
            page.goto(toUrl)
            page.wait_for_timeout(2000)
        
        # 这里可以添加搜索结果处理逻辑
        page.wait_for_timeout(20000)   
        # 使用完后关闭浏览器
        # browser.close()

def wait_for_login_completion(page):
    """等待用户完成登录"""
    max_wait_time = 300  # 最长等待时间（秒）
    check_interval = 2   # 检查间隔（秒）
    start_time = time.time()
    
    print("等待用户完成登录...")
    
    while time.time() - start_time < max_wait_time:
        # 判断是否已经登录成功（不再是登录页面）
        if not page.url.startswith("https://passport.weibo.com/"):
            print("检测到登录成功！")
            # 等待一段时间确保页面完全加载
            page.wait_for_timeout(10000)
            print(page.content())
            return True
        
        # 等待一段时间再检查
        time.sleep(check_interval)
    
    print("等待登录超时！请重新运行程序。")
    return False

def main():
    """主函数"""
    print("启动微博自动化脚本...")
    weibo_login_with_storage_state()

if __name__ == "__main__":
    main()
