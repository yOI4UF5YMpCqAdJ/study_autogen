import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://passport.weibo.com/sso/signin")
    page.get_by_role("textbox", name="手机号").click()
    page.get_by_role("textbox", name="手机号").fill("19370969060")
    page.get_by_role("textbox", name="手机号").press("Tab")
    page.get_by_text("获取验证码").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
