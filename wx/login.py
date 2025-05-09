from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from PIL import Image
import requests
import base64
import json

class WeChatLoginAutomation:
    def __init__(self):
        self.driver = None
        self.qrcode_path = "wechat_qrcode.png"
        
    def setup_driver(self):
        """设置并启动Chrome浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1366,768')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # self.driver.maximize_window()
        
    def navigate_to_login_page(self):
        """导航到微信公众平台登录页面"""
        login_url = "https://mp.weixin.qq.com/"
        self.driver.get(login_url)
        print("已打开微信公众平台登录页面")
        time.sleep(5)
        
    def capture_qrcode_for_mp_weixin(self):
        """专门为微信公众平台登录页面定制的二维码获取方法"""
        print("尝试获取微信公众平台二维码...")
        
        try:
            # 方法集合...（与前一个脚本相同，保留所有获取二维码的方法）
            # 为简洁省略重复代码
            
            # 使用与前一个脚本相同的方法获取二维码
            # 1. iframe方法
            # 2. 直接定位特定元素
            # 3. 从网页获取数据URL
            # 4. 执行JavaScript获取
            # 5. 截取整个页面作为备用
            
            # 示例方法 - 使用JavaScript获取所有可能的二维码图片
            js_code = """
            var images = document.getElementsByTagName('img');
            var qrCodeImages = [];
            for (var i = 0; i < images.length; i++) {
                var img = images[i];
                if (img.src.includes('qrcode') || 
                    (img.parentElement && (img.parentElement.className.includes('qrcode') || img.parentElement.className.includes('scan')))) {
                    qrCodeImages.push(img.src);
                }
            }
            return qrCodeImages;
            """
            qrcode_srcs = self.driver.execute_script(js_code)
            
            if qrcode_srcs and len(qrcode_srcs) > 0:
                print(f"通过JavaScript找到 {len(qrcode_srcs)} 个可能的二维码图片")
                
                for i, src in enumerate(qrcode_srcs):
                    try:
                        print(f"尝试处理第 {i+1} 个二维码链接: {src[:30]}...")
                        
                        if src.startswith('data:image'):
                            # 处理base64编码的图片
                            img_data = src.split(',')[1]
                            img_bytes = base64.b64decode(img_data)
                            with open(self.qrcode_path, 'wb') as f:
                                f.write(img_bytes)
                        else:
                            # 处理URL图片
                            response = requests.get(src)
                            img_bytes = response.content
                            with open(self.qrcode_path, 'wb') as f:
                                f.write(img_bytes)
                        
                        # 验证文件是否为空
                        if os.path.getsize(self.qrcode_path) > 0:
                            print(f"成功从JavaScript获取的URL保存二维码到 {self.qrcode_path}")
                            return True
                    except Exception as e:
                        print(f"处理JavaScript找到的第 {i+1} 个链接时出错: {str(e)}")
                        
            # 最后尝试截取整个页面作为备用
            self.driver.save_screenshot("full_page.png")
            print("已保存整个页面截图到 full_page.png")
            
            return False
            
        except Exception as e:
            print(f"获取二维码过程中发生错误: {str(e)}")
            return False
    
    def push_qrcode_to_mobile(self, token, channel="pushplus"):
        """推送二维码到手机，支持多种渠道"""
        if not os.path.exists(self.qrcode_path) or os.path.getsize(self.qrcode_path) == 0:
            print("错误：二维码文件不存在或为空")
            return False
        
        # 将图片转换为base64
        with open(self.qrcode_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 选择推送渠道
        if channel.lower() == "pushplus":
            return self._push_via_pushplus(token, encoded_string)
        elif channel.lower() == "serverchan":
            return self._push_via_serverchan(token, encoded_string)
        elif channel.lower() == "bark":
            return self._push_via_bark(token, encoded_string)
        else:
            print(f"不支持的推送渠道: {channel}")
            return False
    
    def _push_via_pushplus(self, token, encoded_string):
        """通过PushPlus推送"""
        print("正在通过PushPlus推送二维码到手机...")
        
        # 使用HTML模板，优化在手机上的显示效果
        html_content = f"""
        <div style="text-align:center;">
            <h3 style="color:#07C160;">微信公众号登录二维码</h3>
            <p>请使用<span style="font-weight:bold;color:#07C160;">AutoJS或快捷指令</span>自动处理此通知</p>
            <div style="margin:20px 0;">
                <img src="data:image/png;base64,{encoded_string}" style="max-width:100%;width:300px;" />
            </div>
            <p style="color:#999;font-size:12px;">此消息由自动登录系统发送</p>
        </div>
        """
        
        # 构建推送数据
        data = {
            "token": token,
            "title": "微信公众号登录二维码",
            "content": html_content,
            "template": "html",
            "channel":"sms"

        }
        
        try:
            # 发送请求
            response = requests.post("https://www.pushplus.plus/send", json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("二维码已成功通过PushPlus推送到手机")
                    return True
                else:
                    print(f"推送失败: {result.get('msg', '未知错误')}")
                    return False
            else:
                print(f"推送请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"PushPlus推送失败: {e}")
            return False
    
    def _push_via_serverchan(self, token, encoded_string):
        """通过Server酱推送"""
        print("正在通过Server酱推送二维码到手机...")
        
        # Server酱的API
        url = f"https://sctapi.ftqq.com/{token}.send"
        
        # 构建推送数据
        data = {
            "title": "微信公众号登录二维码",
            "desp": f"![qrcode](data:image/png;base64,{encoded_string})\n\n请使用AutoJS或快捷指令自动处理此通知"
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    print("二维码已成功通过Server酱推送到手机")
                    return True
                else:
                    print(f"推送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"推送请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"Server酱推送失败: {e}")
            return False
    
    def _push_via_bark(self, token, encoded_string):
        """通过Bark推送"""
        print("正在通过Bark推送二维码到手机...")
        
        # Bark API地址
        url = f"{token}/微信公众号登录二维码"
        
        # 构建推送数据
        data = {
            "body": "请使用AutoJS或快捷指令自动处理此通知",
            "icon": "https://mp.weixin.qq.com/favicon.ico",
            "group": "AutoLogin",
            "isArchive": "1",
            "url": f"data:image/png;base64,{encoded_string}"
        }
        
        try:
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("二维码已成功通过Bark推送到手机")
                    return True
                else:
                    print(f"推送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"推送请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"Bark推送失败: {e}")
            return False
    
    def wait_for_login(self, timeout=60):
        """等待登录完成"""
        print(f"等待用户扫码登录，超时时间: {timeout}秒")
        start_time = time.time()
        initial_url = self.driver.current_url
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            # 检查URL是否变化
            if current_url != initial_url:
                print("检测到URL变化，可能已登录")
                # 进一步检查是否在登录后的页面
                if "/home" in current_url or "/media" in current_url:
                    print("登录成功！")
                    return True
            
            # 检查是否有登录成功的元素
            try:
                if len(self.driver.find_elements(By.XPATH, "//a[contains(@href, '/home')]")) > 0:
                    print("检测到导航菜单，登录成功！")
                    return True
            except:
                pass
                
            time.sleep(2)  # 每2秒检查一次
            
        print("等待登录超时")
        return False
        
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")
    
    def run(self, push_config=None):
        """运行完整的自动化流程"""
        try:
            self.setup_driver()
            self.navigate_to_login_page()
            
            # 尝试获取二维码
            qrcode_captured = self.capture_qrcode_for_mp_weixin()
            
            if qrcode_captured:
                print(f"二维码获取成功，保存在 {self.qrcode_path}")
                
                # 如果需要推送到手机
                if push_config:
                    channel = push_config.get("channel", "pushplus")
                    token = push_config.get("token")
                    
                    if token:
                        self.push_qrcode_to_mobile(token, channel)
                    else:
                        print("错误：未提供推送token")
                
                # 等待登录完成
                if self.wait_for_login(120):  # 等待2分钟
                    print("登录流程已完成")
                    
                    # 登录成功后可以执行其他操作
                    # 例如：获取文章列表、发布内容等
                    
                    # 保持会话一段时间
                    keep_alive = input("是否保持会话运行？(y/n): ").lower() == 'y'
                    if keep_alive:
                        minutes = int(input("请输入保持会话时间(分钟): "))
                        print(f"将保持会话 {minutes} 分钟...")
                        time.sleep(minutes * 60)
                else:
                    print("登录失败或超时")
            else:
                print("获取二维码失败，请手动检查网页结构")
                
        finally:
            # 最后关闭浏览器前等待用户确认
            input("按Enter键关闭浏览器...")
            self.close()

if __name__ == "__main__":
    # 创建自动化实例
    automation = WeChatLoginAutomation()
    
    # 推送配置
    # 支持的渠道: "pushplus", "serverchan", "bark"
    push_config = {
        "channel": "pushplus",  # 使用的推送渠道
        "token": "80b5371ed3324d74b7a893e2d33c6608"  # 替换为您的token
    }
    
    # 运行自动化流程
    automation.run(None)