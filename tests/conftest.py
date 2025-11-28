
import pytest
import allure
import logging
from playwright.sync_api import sync_playwright, Cookie
import os
import re
# tests/conftest.py 最顶部添加（先导入 sys 和 Path）
import sys
from pathlib import Path

# 获取项目根目录（fireworks/）：conftest.py 的父目录（tests/）的父目录
project_root = Path(__file__).resolve().parent.parent
# 把项目根目录添加到 sys.path 最前面（优先搜索）
sys.path.insert(0, str(project_root))

# 之后再导入 HomePage（原代码不变）
from tests.pages.home_page import HomePage
# ... 其他原有代码
import allure

from tests.pages.home_page import HomePage
from tests.pages.transport_license_application_page import *

# 确保截图目录存在
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def sanitize_filename(name):
    """
    清洗文件名，移除或替换所有可能导致路径问题的特殊字符
    """
    # 替换Windows系统不允许的文件名特殊字符
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)
    # 替换空格和Unicode字符
    sanitized = re.sub(r'\s+', '_', sanitized)
    # 限制文件名长度，避免路径过长
    max_length = 120
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    return sanitized

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """钩子函数：捕获测试结果并在失败时截图"""
    outcome = yield
    report = outcome.get_result()

    # 只处理测试用例失败的情况，且测试函数需要page参数
    if report.when == "call" and report.failed and "page" in item.fixturenames:
        # 获取page对象
        page = item.funcargs["page"]

        # 生成唯一的截图文件名（包含时间戳和测试用例名）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清洗测试用例名称，移除特殊字符
        test_name = sanitize_filename(item.nodeid.replace("::", "_").replace("/", "_"))
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"failed_{test_name}_{timestamp}.png")

        try:
            # 保存截图
            page.screenshot(path=screenshot_path)
            print(f"\n测试失败，已保存截图至：{screenshot_path}")
        except Exception as e:
            print(f"\n保存截图失败：{str(e)}")

        # 2. 新增：将截图附加到Allure报告
        try:
            # 截取全屏（full_page=True），返回二进制字节流（无需生成临时文件）
            screenshot_bytes = page.screenshot(full_page=True)
            # 调用allure.attach()将二进制流附加到报告
            allure.attach(
                body=screenshot_bytes,  # 截图二进制数据
                name=f"Failed_Screenshot_{test_name}_{timestamp}",  # 报告中显示的附件名称（含用例名+时间戳，避免重复）
                attachment_type=allure.attachment_type.PNG  # 指定附件类型为PNG，确保报告能正确渲染图片
            )
        except Exception as e:
            print(f"\n附加截图到Allure报告失败：{str(e)}")

@pytest.fixture(autouse=True)
def configure_logging():
    # 配置基本日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 获取日志记录器
    logger = logging.getLogger('conf.logging_config')  # 与你的日志名称匹配
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        # 旧版本Playwright忽略HTTPS错误的实现方式
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--window-size=1920,1080",
                "--disable-dev-shm-usage",
                "--disable-javascript-breakpoints"  # 禁用JS断点
            ]
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(ignore_https_errors=True)

    # 注入Cookie
    cookie: Cookie = {
        "name": "JSESSIONID",
        "value": "81416546E118663AA085C76E82C8FDE6",
        "domain": "192.168.50.53",
        "path": "/",
        "secure": True,
        "httpOnly": True
    }
    context.add_cookies([cookie])

    page = context.new_page()  # 使用实际窗口大小
    yield page
    page.close()
    context.close()  # 关闭context

@pytest.fixture(scope="session")
def base_url():
    return "https://192.168.50.53:16443/yhbzglxt-qy/index.do"

@pytest.fixture(scope="session")
def test_password():
    return {
        "password": "1"
    }

@pytest.fixture(scope="function")
def transport_license_setup(page, base_url):
    """免密登录"""
    page.goto(base_url, timeout=10000)
    home_page = HomePage(page)
    home_page.navigate_to_page("许可证管理")
    return TransportLicenseApplicationPage(page)

def pytest_configure(config):
    # 注册更多自定义标记
    config.addinivalue_line("markers", "register: 标记注册流程相关的测试用例")
