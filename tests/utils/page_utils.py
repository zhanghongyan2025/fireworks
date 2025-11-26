import re
import datetime
from playwright.sync_api import Page, FrameLocator
# 假设你的 logging_config 配置正确
from conf.logging_config import logger


def get_top_frame_content(page: Page) -> FrameLocator:
    """
    获取 topFrame 框架定位器。
    路径: #leftFrame -> (content) -> [title="topFrame"]
    """
    return page.locator("#leftFrame").content_frame.get_by_title("topFrame").content_frame


def get_main_frame_content(page: Page) -> FrameLocator:
    """
    获取 mainFrame 框架定位器。
    路径: #leftFrame -> (content) -> [title="mainFrame"]
    """
    return page.locator("#leftFrame").content_frame.get_by_title("mainFrame").content_frame


def get_table_main_frame_content(page: Page) -> FrameLocator:
    """
    获取 table_main 框架定位器。
    路径: #leftFrame -> mainFrame -> (content) -> frame[name="table_main"]
    """
    # 先获取 mainFrame
    main_frame = get_main_frame_content(page)
    # 从 mainFrame 内继续查找 table_main
    return main_frame.locator("frame[name=\"table_main\"]").content_frame


def get_calender_frame_content(page: Page) -> FrameLocator:
    """
    获取日期选择器所在的框架（table_main_frame -> div#_my97DP -> iframe）。

    :param page: Playwright 的 Page 对象。
    :return: 日期选择器 iframe 的 FrameLocator 对象。
    """
    # 1. 先获取到 table_main 框架
    table_main_frame = get_table_main_frame_content(page)

    # 2. 在 table_main 框架内定位日期选择器容器 div#_my97DP，再获取其下的 iframe
    calendar_iframe_locator = table_main_frame.locator("div#_my97DP").locator("iframe")

    # 3. 转换为 FrameLocator 并返回
    return calendar_iframe_locator.content_frame


def get_calendar_month(page: Page) -> str:
    """
    获取当前日历选择器中显示的月份。

    :param page: Playwright 的 Page 对象。
    :return: 当前显示的月份（例如 "十一" 代表11月）。
    """
    calendar_frame = get_calender_frame_content(page)
    month_input_locator = calendar_frame.locator(
        "xpath=//*[contains(@class, 'menuSel') and contains(@class, 'MMenu')]/following-sibling::input[1]"
    )
    month_input_locator.wait_for(state="visible", timeout=5000)
    return month_input_locator.input_value()


def get_calendar_year(page: Page) -> str:
    """
    获取当前日历选择器中显示的年份。

    :param page: Playwright 的 Page 对象。
    :return: 当前显示的年份（例如 "2025"）。
    """
    calendar_frame = get_calender_frame_content(page)
    year_input_locator = calendar_frame.locator(
        "xpath=//*[contains(@class, 'menuSel') and contains(@class, 'YMenu')]/following-sibling::input[1]"
    )
    year_input_locator.wait_for(state="visible", timeout=5000)
    return year_input_locator.input_value()


def is_calendar_year_month_display_correct(page: Page) -> bool:
    """
    检查日历显示的年份（阿拉伯数字）和月份（中文）是否为当前系统的年和月。
    如果不匹配，则抛出 AssertionError。

    :param page: Playwright 的 Page 对象。
    :return: 若显示正确则返回 True。
    :raises AssertionError: 当年或月不匹配时抛出。
    """
    # 1. 获取当前系统的日期（仅日期部分）
    current_date_obj = datetime.datetime.now().date()
    expected_year = str(current_date_obj.year)

    chinese_months = {
        1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六",
        7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"
    }
    expected_month = chinese_months[current_date_obj.month]

    # 2. 获取日历显示的年和月
    try:
        displayed_year = get_calendar_year(page)
        displayed_month = get_calendar_month(page)
    except Exception as e:
        raise AssertionError(f"获取日历信息失败: {e}") from e

    # 3. 验证年和月是否匹配
    assert displayed_year == expected_year, \
        f"年份不匹配！当前系统年份: {expected_year}, 日历显示年份: {displayed_year}"

    assert displayed_month == expected_month, \
        f"月份不匹配！当前系统月份: {expected_month}月, 日历显示月份: {displayed_month}"

    # 4. 打印成功信息并返回
    logger.info(f"日历显示正确：{expected_year}年{expected_month}月")
    return True


def is_calendar_display_correctly(page: Page) -> bool:
    """
    根据提供的HTML结构，验证日历显示是否正确。
    1. 过去的日期应只有 'WinvalidDay' class，且无 onclick。
    2. 今天及未来的日期不应有 'WinvalidDay' class，且有正确格式的 onclick。

    :param page: Playwright 的 Page 对象。
    :return: 如果所有检查都通过，返回 True；否则返回 False。
    """
    # 1. 获取当前系统日期（仅日期部分）
    today = datetime.datetime.now().date()
    logger.info(f"当前系统日期: {today}")

    # 2. 获取日历框架
    try:
        calendar_frame = get_calender_frame_content(page)
    except Exception as e:
        logger.error(f"获取日历框架失败: {e}")
        return False

    # 3. 定位所有日期行
    date_rows = calendar_frame.locator("table.WdayTable > tbody > tr").nth(1).locator("xpath=following-sibling::tr")
    if date_rows.count() == 0:
        logger.warning("未找到任何日期行。")
        return False

    all_checks_passed = True

    # 4. 遍历检查每个日期单元格
    for i in range(date_rows.count()):
        row = date_rows.nth(i)
        cells = row.locator("td")
        for j in range(cells.count()):
            cell = cells.nth(j)
            cell_text = cell.text_content().strip()
            if not cell_text:
                continue

            is_past = False
            is_future_or_today = False
            cell_date = None

            onclick_attr = cell.get_attribute("onclick")
            if onclick_attr:
                match = re.search(r'day_Click\((\d+),\s*(\d+),\s*(\d+)\)', onclick_attr)
                if match:
                    year, month, day = map(int, match.groups())
                    cell_date = datetime.date(year, month, day)
                    if cell_date < today:
                        is_past = True
                    else:
                        is_future_or_today = True
            else:
                is_past = True  # 没有onclick的默认为过去日期

            cell_classes = cell.get_attribute("class")

            if is_past:
                if cell_classes != "WinvalidDay":
                    logger.error(
                        f"❌ 检查失败: 日期 {cell_text} 是过去的日期，但class为 '{cell_classes}' (应为 'WinvalidDay')。")
                    all_checks_passed = False
                if onclick_attr:
                    logger.error(f"❌ 检查失败: 日期 {cell_text} 是过去的日期，但含有 onclick 属性 '{onclick_attr}'。")
                    all_checks_passed = False

            if is_future_or_today:
                if "WinvalidDay" in cell_classes:
                    logger.error(
                        f"❌ 检查失败: 日期 {cell_text} ({cell_date}) 是今天或未来的日期，但class包含 'WinvalidDay'。")
                    all_checks_passed = False
                if not onclick_attr:
                    logger.error(f"❌ 检查失败: 日期 {cell_text} ({cell_date}) 是今天或未来的日期，但缺少 onclick 属性。")
                    all_checks_passed = False

    if all_checks_passed:
        logger.info("✅ 所有日期显示检查均通过。")

    return all_checks_passed


def select_calendar_date(page: Page, target_date: datetime.date = None):
    """
    在日历中选择指定的日期。

    :param page: Playwright 的 Page 对象。
    :param target_date: 要选择的日期（datetime.date 对象）。如果为 None，则默认选择当前日期。
    """
    # 1. 确定目标日期
    if target_date is None:
        target_date = datetime.date.today()
        logger.info(f"未指定日期，将选择当前日期：{target_date}")
    else:
        logger.info(f"准备在日历中选择日期：{target_date}")

    target_year, target_month, target_day = target_date.year, target_date.month, target_date.day

    # 2. 获取日历框架
    try:
        calendar_frame = get_calender_frame_content(page)
    except Exception as e:
        logger.error(f"获取日历框架失败：{str(e)}")
        raise

    # 3. 定位并点击目标日期单元格
    xpath_expression = (
        f"//td[contains(@onclick, 'day_Click({target_year},{target_month},{target_day})')]"
    )
    target_date_cell = calendar_frame.locator(f"xpath={xpath_expression}")

    try:
        target_date_cell.wait_for(state="visible", timeout=10000)
        target_date_cell.click()
        logger.info(f"成功选择日期：{target_date}")
    except Exception as e:
        logger.error(f"选择日期 {target_date} 失败：{str(e)}")
        raise