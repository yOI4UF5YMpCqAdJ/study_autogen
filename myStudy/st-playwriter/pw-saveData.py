"""
使用Python版Playwright的Storage State功能保存微博登录状态
"""
import os
import json
from playwright.sync_api import sync_playwright
import time
import re
from pathlib import Path
import ddddocr
import cv2
import numpy as np

toUrl = "https://s.weibo.com/weibo?q=%E6%9C%88%E8%96%AA%E4%B8%89%E5%8D%834%E5%B9%B4%E5%AD%98%E4%BA%8610%E4%B8%87%E5%9D%97"

def weibo_login_with_storage_state():
    """使用存储状态保存和恢复微博登录会话"""
    
    # 存储状态的文件路径
    storage_state_path = Path(__file__).parent.parent.parent /'weibo/weibo_storage_state.json'
   

    with sync_playwright() as p:
        browser_type = p.chromium
        # 启动浏览器
        browser = browser_type.launch(headless=False)

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
        
        # 访问微博首页
        # login https://passport.weibo.com/sso/signin
        page.goto(toUrl)
        page.wait_for_timeout(2000)

        if page.url.startswith("https://passport.weibo.com/"):
            weibo_login(page)
            return
           

def weibo_login(page):
    page.get_by_role("link", name="账号登录").click()
    txtPhone = page.get_by_role("textbox", name="手机号")
    page.get_by_role("textbox", name="手机号").click()
    page.get_by_role("textbox", name="手机号").fill("19370659060")
    page.get_by_role("textbox", name="手机号或邮箱").press("Tab")
    page.get_by_role("textbox", name="密码").fill("edifier")
    page.get_by_role("textbox", name="手机号或邮箱").click()
    page.get_by_role("button", name="登录").click()
    page.wait_for_timeout(3000)

    # 检测验证码 
    captcha_element = check_captcha(page)
    if captcha_element:
        # 获取验证码图片和提示
       captcha_path, tips_paths = capture_captcha_info(page)
       if captcha_path:
         click_positions = analyze_word_captcha(captcha_path,tips_paths)
         if click_positions:
            # 点击验证码
            for i, (pos_x, pos_y) in enumerate(click_positions):
                box = page.locator(".geetest_bg").bounding_box()
                if box:
                    abs_x = box["x"] + pos_x 
                    abs_y = box["y"] + pos_y
                # 点击 
                print(f"点击位置 {i+1}: ({abs_x}, {abs_y})") 
                page.mouse.click(abs_x, abs_y) 
                page.wait_for_timeout(800) # 点击间隔

            print(click_positions)

            #点击确定

        

 
    pass

def check_captcha(page):
    """检测页面是否存在验证码"""
    try:
        # 基于您提供的HTML，使用精确的选择器
        captcha_selector = ".geetest_box"
        
        # 等待并检查验证码是否出现（最多等待5秒）
        captcha_visible = page.wait_for_selector(captcha_selector, state="visible", timeout=5000)
        
        if captcha_visible:
            print("检测到验证码")
            return captcha_visible
        else:
            print("未检测到验证码")
            return None
    except Exception as e:
        print(f"检测验证码时出错: {e}")
        return None

def capture_captcha_info(page):
    """获取验证码图片和需要点击的提示"""
    try:
        # 创建临时目录
        temp_dir = Path(__file__).parent.parent.parent/"weibo/temp/"
        
        # 1. 获取主验证码图片
        bg_element = page.locator(".geetest_bg")
        if not bg_element.is_visible():
            print("验证码背景图不可见")
            return None, []
            
        # 获取背景图片URL (从style属性中提取)
        bg_style = bg_element.get_attribute("style")
        bg_url_match = re.search(r'url\("([^"]+)"\)', bg_style)
        if not bg_url_match:
            print("无法获取验证码背景图URL")
            return None, []
            
        bg_url = bg_url_match.group(1)
        print(f"验证码背景图URL: {bg_url}")
        
        # 下载背景图片
        captcha_path = os.path.join(temp_dir, f"weibo_captcha_bk.jpg")
        # 使用playwright下载图片
        response = page.request.get(bg_url)
        with open(captcha_path, "wb") as f:
                f.write(response.body())
                
        print(f"验证码图片已保存到: {captcha_path}")
        
        # 2. 获取需要点击的提示图片
        tips_elements = page.locator(".geetest_ques_tips img").all()
        tips_paths = []
        for i, tip_elem in enumerate(tips_elements):
            tip_url = tip_elem.get_attribute("src")
            # 下载提示图片
            tip_path = os.path.join(temp_dir, f"weibo_captcha_tip_{i}.png")
            tip_response = page.request.get(tip_url)
            with open(tip_path, "wb") as f:
                f.write(tip_response.body())
            print(f"要求图片 {i+1} 已保存到: {tip_path}")
            tips_paths.append(tip_path)

        return captcha_path, tips_paths
    except Exception as e:
        print(f"获取验证码信息时出错: {e}")
        return None, []

def analyze_word_captcha(captcha_path, tips_paths):
    """
    分析文字类型的验证码（极验验证码）
    根据提示图片内容，在验证码图片中找到对应位置
    
    参数:
    captcha_path: 验证码主图片路径
    tips_paths: 提示图片路径列表
    
    返回:
    click_positions: 需要点击的位置坐标列表[(x1,y1), (x2,y2), ...]
    """
    ocr = ddddocr.DdddOcr(det=True)
    try:
        # 1. 读取验证码主图片
        captcha_img = cv2.imdecode(np.fromfile(captcha_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        #  = cv2.imread(captcha_path)
        if captcha_img is None:
            print(f"无法读取验证码图片: {captcha_path}")
            return []
            
        # 在验证码图上进行文本检测
        with open(captcha_path, 'rb') as f:
            captcha_bytes = f.read()
        
        # 使用ddddocr检测验证码图片中的所有可能目标
        all_bboxes = ocr.detection(captcha_bytes)
        print(f"在验证码图片中检测到 {len(all_bboxes)} 个潜在目标")
        
        # 如果没有检测到目标，返回空列表
        if not all_bboxes:
            print("未检测到任何目标，可能需要其他方法")
            return []
        
        # 2. 处理每个提示图片，提取特征
        tip_features = []
        for i, tip_path in enumerate(tips_paths):
            if not os.path.exists(tip_path):
                print(f"提示图片不存在: {tip_path}")
                continue
                
            # 读取提示图片
            with open(tip_path, 'rb') as f:
                tip_bytes = f.read()
                
            try:
                # 使用文字识别模式获取提示内容
                tip_text = ddddocr.DdddOcr(show_ad=False).classification(tip_bytes)
                print(f"提示图片 {i+1} 识别结果: {tip_text}")
                tip_features.append(tip_text)
            except Exception as e:
                print(f"识别提示图片 {i+1} 出错: {e}")
                
        # 如果没有成功提取任何提示特征，返回空列表
        if not tip_features:
            print("未能提取提示特征，返回空结果")
            return []
            
        # 3. 在验证码图片中检测的文本目标中查找与提示匹配的内容
        # 为每个检测到的区域提取文本
        detected_texts = []
        detected_positions = []
        
        for bbox in all_bboxes:
            x1, y1, x2, y2 = bbox
            # 从验证码图片中裁剪出这个区域
            roi = captcha_img[y1:y2, x1:x2]
            
            # 将ROI保存为临时文件
            temp_roi_path = f"temp_roi_{x1}_{y1}.png"
            cv2.imwrite(temp_roi_path, roi)
            
            try:
                # 读取临时文件并识别文本
                with open(temp_roi_path, 'rb') as f:
                    roi_bytes = f.read()
                
                # 识别文本
                roi_text = ddddocr.DdddOcr(show_ad=False).classification(roi_bytes)
                print(f"区域 ({x1},{y1},{x2},{y2}) 识别结果: {roi_text}")
                
                # 记录识别结果和位置
                detected_texts.append(roi_text)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                detected_positions.append((center_x, center_y))
            except Exception as e:
                print(f"识别区域出错: {e}")
            finally:
                # 删除临时文件
                if os.path.exists(temp_roi_path):
                    os.remove(temp_roi_path)
        
        # 4. 根据提示内容匹配验证码中的文本，获取需要点击的位置
        click_positions = []
        for tip_text in tip_features:
            best_match = None
            best_score = 0
            best_index = -1
            
            # 简单的文本匹配策略：寻找包含提示文本的区域
            for i, detected_text in enumerate(detected_texts):
                # 计算匹配度（简单实现）
                if tip_text in detected_text or detected_text in tip_text:
                    # 完全匹配权重更高
                    if tip_text == detected_text:
                        score = 1.0
                    # 部分匹配
                    else:
                        score = len(set(tip_text) & set(detected_text)) / max(len(tip_text), len(detected_text))
                        
                    if score > best_score:
                        best_score = score
                        best_match = detected_positions[i]
                        best_index = i
            
            # 如果找到匹配，添加到点击位置
            if best_match:
                click_positions.append(best_match)
                print(f"提示 '{tip_text}' 匹配到区域 {best_index+1}，坐标: {best_match}")
        
        # 如果没有找到任何匹配，尝试使用备用策略
        if not click_positions and all_bboxes:
            print("未找到与提示匹配的内容，使用备用策略")
            # 备用策略：返回前N个检测到的目标位置（N等于提示图片数量）
            for i in range(min(len(all_bboxes), len(tips_paths))):
                x1, y1, x2, y2 = all_bboxes[i]
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                click_positions.append((center_x, center_y))
                print(f"备用策略：选择区域 {i+1}，坐标: ({center_x}, {center_y})")
        
        # 为了调试，在验证码图片上标记检测到的目标和需要点击的位置
        debug_img = captcha_img.copy()
        
        # 标记所有检测到的目标
        for bbox in all_bboxes:
            x1, y1, x2, y2 = bbox
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
        # 标记需要点击的位置
        for i, (x, y) in enumerate(click_positions):
            cv2.circle(debug_img, (x, y), 10, (0, 0, 255), -1)
            cv2.putText(debug_img, str(i+1), (x-5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        # 保存调试图片
        debug_path = captcha_path.replace('.jpg', '_debug.jpg').replace('.png', '_debug.png')
        cv2.imwrite(debug_path, debug_img)
        print(f"调试图片已保存到: {debug_path}")
        
        return click_positions
        
    except Exception as e:
        print(f"分析验证码时出错: {e}")
        return []




def main():
    """主函数"""
    print("启动微博自动化脚本...")
    weibo_login_with_storage_state()


if __name__ == "__main__":
    main()