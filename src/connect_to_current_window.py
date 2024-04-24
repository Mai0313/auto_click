from playwright.sync_api import sync_playwright


def take_screenshot_from_remote_browser():
    with sync_playwright() as playwright:
        # 连接到运行在指定端口上的远程Chrome实例
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")

        # 获取当前的浏览器上下文和页面
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            # 截图并保存
            page.screenshot(path="screenshot.png")
            # print("截图已保存为screenshot.png")
        else:
            # print("没有找到任何浏览器上下文。")
            pass

        # 在完成操作后关闭浏览器连接
        browser.close()


take_screenshot_from_remote_browser()
