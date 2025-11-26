import os
import random
import time

from werkzeug.serving import select_address_family

from conf.logging_config import logger
from playwright.sync_api import Page, sync_playwright, expect
import datetime

from tests.pages.home_page import HomePage
from tests.utils.page_utils import *


class licenseManagementPage:
    """运输证管理页面自动化测试类"""

    def __init__(self, page: Page):
        """
        初始化icenseManagementPage类

        Args:
            page (Page): Playwright的Page对象，用于操作浏览器页面
        """
        self.page = page
        self.table_main_frame_content = get_table_main_frame_content(self.page)

    def select_import_export_status(self, status_type: str):
        """
        根据状态类型字符串，选择“进出口状态”下拉菜单中的对应选项。

        :param self: 类实例的引用。
        :param status_type: 状态类型字符串，可选值为: "出口", "购买", "配送", "退货", "本单位运输"。
        """
        # 1. 定义一个映射字典，将状态类型字符串与下拉框的value值关联起来。
        #    这使得代码易于阅读和维护。
        status_mapping = {
            "出口": "0",
            "购买": "1",
            "配送": "2",
            "退货": "3",
            "本单位运输": "5"
        }

        # 2. 检查传入的 status_type 是否有效。
        if status_type not in status_mapping:
            valid_statuses = ", ".join(status_mapping.keys())
            error_message = f"无效的状态类型: '{status_type}'。请从以下有效状态中选择: {valid_statuses}"
            logger.error(error_message)
            # 可以选择抛出异常，让调用者知道发生了错误。
            raise ValueError(error_message)

        # 3. 根据映射字典获取对应的 value。
        target_value = status_mapping[status_type]

        # 4. 执行选择操作。
        logger.info(f"正在选择进出口状态: '{status_type}' (对应值: {target_value})")

        # 确保 table_main_frame 已经被正确初始化和定位
        # 这里假设 self.table_main_frame 是一个已经定位好的 Playwright Locator 对象
        status_selector = self.table_main_frame_content.locator("#jckzt")

        # 使用 select_option 方法通过 value 来选择选项
        status_selector.select_option(value=target_value)

        logger.info(f"成功选择进出口状态: '{status_type}'")

    def trigger_search_popup(
            self,
            title: str,
            need_click_search_: bool = True,
            id: str = ""
    ):
        """
        根据提供的参数，在弹窗中执行相应的操作。

        1. 如果 need_click_search_ 为 True:
            a. 首先点击 name 属性为 title 的 textbox。
            b. 然后找到该 textbox 的第一个兄弟 input 节点并点击。
        2. 如果 need_click_search_ 为 False:
            a. 如果 id 参数不为空，则点击 id 为该值的元素。
            b. 如果 id 参数为空，则点击 name 属性为 title 的 textbox。

        :param self: 类实例的引用。
        :param title: 用于定位 textbox 的 name 属性值。
        :param need_click_search_: 是否需要执行搜索操作。
        :param id: (可选) 用于定位元素的 id 属性值。
        """
        logger.info(f"开始处理弹窗操作。title: '{title}', need_click_search_: {need_click_search_}, id: '{id}'")

        try:
            if need_click_search_:
                logger.info("need_click_search_ 为 True，准备执行搜索操作...")

                # 步骤 1a: 找到 name 属性为 title 的 textbox
                textbox = self.table_main_frame_content.get_by_role("textbox", name=title, exact=True)
                # 步骤 1b: 找到该 textbox 的第一个兄弟 input 节点并点击
                logger.info(f"寻找 textbox (name='{title}') 的第一个兄弟 input 节点...")
                # 使用 XPath 的 following-sibling 轴来查找紧邻的下一个 input 元素
                search_button = textbox.locator("xpath=following-sibling::input[1]")
                search_button.wait_for(state="visible", timeout=5000)
                logger.info("已找到查询按钮。")
                search_button.click()

            else:
                logger.info("need_click_search_ 为 False，准备执行选择操作...")

                if id:
                    # 步骤 2a: 如果 id 不为空，则点击 id 为该值的元素
                    logger.info(f"id 参数不为空，准备点击元素 (id='{id}')...")
                    element_by_id = self.table_main_frame_content.locator(f"#{id}")
                    element_by_id.wait_for(state="visible", timeout=5000)
                    element_by_id.click()
                    logger.info(f"已点击元素 (id='{id}')。")

                else:
                    # 步骤 2b: 如果 id 为空，则点击 name 属性为 title 的 textbox
                    logger.info(f"id 参数为空，准备点击 textbox (name='{title}')...")
                    textbox = self.table_main_frame_content.get_by_role("textbox", name=title, exact=True)
                    textbox.wait_for(state="visible", timeout=5000)
                    textbox.click()
                    logger.info(f"已点击 textbox (name='{title}')。")

        except Exception as e:
            logger.error(f"处理弹窗操作时发生未知错误: {e}")
            self.page.screenshot(path="handle_popup_actions_general_error.png")
            raise

    def select_redential_PSB(self, location_type: str):
        """
        在“证件管理类型”中，根据地点类型勾选对应的县级公安机关复选框。

        :param self: 类实例的引用。
        :param location_type: 地点类型，可选值为 '起运地县级公安机关' 或 '运达地县级公安机关'。
        """
        # 注意：你的原始代码片段中使用了 'organization_code'，但函数参数是 'location_type'。
        # 这里我假设日志信息应该与函数功能匹配。
        logger.info(f"开始执行操作：选择地点类型 '{location_type}'...")

        try:
            # 等待页面网络空闲和内容渲染
            self.page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)  # 增加一个短暂的等待，作为网络空闲后的补充保险

            # 监听并自动关闭可能出现的对话框
            self.page.once("dialog", lambda dialog: dialog.dismiss())

            # 根据 location_type 确定要勾选的复选框
            if location_type == "起运地县级公安机关":
               self.table_main_frame_content.locator("#kzjglx").first.check()
            elif location_type == "运达地县级公安机关":
               self.table_main_frame_content.locator("#kzjglx").nth(1).check()
            else:
                raise ValueError(
                    f"不支持的地点类型: '{location_type}'。请使用 '起运地县级公安机关' 或 '运达地县级公安机关'。")
            logger.info(f"成功勾选 '{location_type}' 的复选框。")

        except Exception as e:
            logger.error(f"选择 '{location_type}' 时发生未知错误: {e}")
            self.page.screenshot(path="select_PSB_error.png")
            raise

    def select_start_transport_time(self):
        calender_frame = get_calender_frame_content(self.page)
        calendar_month = get_calendar_month(self.page)
        calendar_year = get_calendar_year(self.page)
        self.table_main_frame_content.get_by_role("textbox", name="运输起始时间").click()

        is_calendar_year_month_display_correct(self.page)
        is_calendar_display_correctly(self.page)
        select_calendar_date(self.page)

    def select_end_transport_time(self):
        """
        随机选择一个未来或今天的日期作为运输截止时间。
        该函数会查找所有包含 onclick="day_Click(...)" 的 td 元素，并随机点击一个。
        """
        self.table_main_frame_content.get_by_role("textbox", name="运输截止时间").click()
        logger.info("开始随机选择运输截止时间...")

        # 1. 获取日历所在的 iframe 框架
        try:
            calendar_frame = get_calender_frame_content(page)  # 复用之前的框架获取函数
        except Exception as e:
            logger.error(f"获取日历框架失败：{str(e)}")
            raise

        # 2. 定位所有包含 onclick="day_Click(...)" 的 td 元素
        # 使用 XPath 查找所有具有 onclick 属性且属性值符合 day_Click 格式的 td
        xpath_expression = "//td[contains(@onclick, 'day_Click')]"
        clickable_dates = calendar_frame.locator(f"xpath={xpath_expression}")

        # 4. 获取可点击日期的数量
        date_count = clickable_dates.count()
        if date_count == 0:
            logger.error("未找到任何可点击的日期。")
            raise Exception("日历中没有可供选择的未来日期。")

        logger.info(f"找到 {date_count} 个可选择的日期。")

        # 5. 随机选择一个日期的索引
        random_index = random.randint(0, date_count - 1)
        logger.info(f"随机选择第 {random_index + 1} 个日期。")

        # 6. 定位并点击随机选择的日期单元格
        selected_date_cell = clickable_dates.nth(random_index)

        # 获取并打印选中的日期文本（例如 "25"）
        selected_day_text = selected_date_cell.text_content().strip()
        logger.info(f"准备选择日期：{selected_day_text} 日")

        selected_date_cell.click()
        logger.info(f"成功选择运输截止日期：{selected_day_text} 日")

        # 可选：返回选中的日期对象
        # 从 onclick 属性中解析出完整日期
        onclick_attr = selected_date_cell.get_attribute("onclick")
        if onclick_attr:
            match = re.search(r'day_Click\((\d+),\s*(\d+),\s*(\d+)\)', onclick_attr)
            if match:
                year, month, day = map(int, match.groups())
                selected_date = datetime.date(year, month, day)
                logger.info(f"解析选中的完整日期为：{selected_date}")
                return selected_date

        return None

    def query_fill_input(self,  unit_name: str):
        """
        根据提供的单位名称（unit_namee），完成查询并选择对应的数据行。

        步骤：
        1. 在查询表单的“单位名称”输入框中填入 unit_name。
        2. 点击“查询”按钮。
        3. 等待结果表格加载。
        4. 在结果表格中定位并点击单位代码匹配的行。

        :param self: Page 对象实例。
        :param unit_name: 要查询和选择的单位名称。
        """

        logger.info(f"开始执行操作：查询并选择单位名称 '{unit_name}'...")

        try:

            # 等待弹窗内的框架加载
            time.sleep(1)

            # 获取零售单位选择弹窗的框架内容 (是第4个iframe, nth(3))
            #retail_select_content = self.table_main_frame_content.locator("iframe").nth(3).content_frame

            retail_select_content = self.table_main_frame_content.locator("iframe").nth(3).content_frame

            # 正确的代码：定位最后一个 iframe
            retail_select_content = self.table_main_frame_content.locator("iframe").last.content_frame

            # 6. 填入单位名称并查询
            unit_name_input = retail_select_content.get_by_role("row", name="单位名称：", exact=True).get_by_role("textbox")
            unit_name_input.fill(unit_name)
            logger.info(f"已在查询框中填入单位名称: {unit_name}")

            query_button = retail_select_content.get_by_role("button", name="查询")
            query_button.click()
            logger.info("已点击 '查询' 按钮。")

            # 7. 等待结果并选择
            result_row = retail_select_content.get_by_role("row", name=unit_name)
            logger.info(f"查询结果已加载，找到单位名称 '{unit_name}'。")
            time.sleep(1)
            result_row.dblclick()
            logger.info(f"已成功选择单位代码为 '{unit_name}' 的行。")

        except Exception as e:
            logger.error(f"在执行操作时发生错误: {e}", exc_info=True)
            # 可以在这里添加截图等错误处理逻辑
            raise  # 将异常向上抛出，以便调用者处理

    def fill_consignor_info(
            self,
            consigning_party_responsible_person_name: str,
            consignor_responsible_person_phone: str,
            consignor_handler_name: str,
            consignor_handler_id_card: str,
            consignor_handler_contact_phone: str
    ):
        """
        填写托运人信息表单。

        Args:
            self: 类的实例对象。
            consigning_party_responsible_person_name (str): 托运单位负责人姓名。
            consignor_responsible_person_phone (str): 托运单位负责人电话。
            consignor_handler_name (str): 托运经办人姓名。
            consignor_handler_id_card (str): 托运经办人身份证号。
            consignor_handler_contact_phone (str): 托运经办人联系电话。
        """
        # 使用预先获取的 frame content 对象，简化后续定位
        frame_content = self.table_main_frame_content

        # 1. 填写托运负责人姓名
        frame_content.get_by_role("textbox", name="托运负责人", exact=True).fill(
            consigning_party_responsible_person_name)

        # 2. 填写托运负责人电话
        frame_content.get_by_role("textbox", name="托运负责人电话").fill(consignor_responsible_person_phone)

        # 3. 填写经办人姓名
        time.sleep(1)
        frame_content.get_by_role("textbox", name="经办人姓名", exact=True).fill(consignor_handler_name)

        # 4. 填写经办人身份证号
        frame_content.get_by_role("textbox", name="经办人身份证号").fill(consignor_handler_id_card)

        # 5. 填写经办人联系电话
        frame_content.get_by_role("textbox", name="经办人联系电话").fill(consignor_handler_contact_phone)

    def add_delivered_goods(
            self,
            item_option: str,
            product_specification: str,
            numbers_per_carton: str,
            carton_quantity: str
    ):
        """
        添加已配送物品的操作函数，利用page_utils中的框架定位函数简化定位逻辑。
        所有可变数据均通过参数传入。

        :param item_option: 物品选择下拉框中的选项值 (例如: "172--进疆礼花弹A--1--04--3#礼花弹--进疆礼花弹A--A级--3")
        :param product_specification: 产品规格 (对应 gg21 输入框)
        :param numbers_per_carton: 箱含量 (对应 gg31 输入框)
        :param carton_quantity: 数量(箱) (对应 gg11 输入框)
        """
        # 获取table_main框架定位器，替代重复的框架定位代码
        table_main_frame = get_table_main_frame_content(self.page)

        # 执行物品选择操作
        table_main_frame.locator("#temp1").select_option(item_option)

        # 操作gg21输入框（产品规格）
        product_specification_locator = table_main_frame.locator("input[name=\"gg21\"]")
        product_specification_locator.fill(product_specification)

        # 操作gg31输入框（箱含量）
        numbers_per_carton_locator = table_main_frame.locator("input[name=\"gg31\"]")
        numbers_per_carton_locator.fill(numbers_per_carton)

        # 操作gg11输入框（数量(箱)）
        carton_number_locator = table_main_frame.locator("input[name=\"gg11\"]")
        carton_number_locator.fill(carton_quantity)

        # 以下为你注释掉的代码，如果需要启用，也可以考虑是否将按钮文本作为参数
        # # 点击增加配送物品按钮
        # table_main_frame.get_by_role("button", name="+ 增加配送物品").click()
        #
        # # 点击物品查询相关链接
        # table_main_frame.get_by_role(
        #     "row",
        #     name="物品查询 箱 *",
        #     exact=True
        # ).get_by_role("link").click()

    def select_transport_vehicle_plate(self, plate_number: str) -> None:
        """
        选择运输车辆牌号（在类中使用）

        参数:
            self: 类的实例
            plate_number: 要选择的车牌号（如 "H5515"）
        """
        try:
            logger.info(f"开始选择运输车辆牌号: {plate_number}")

            # 1. 通过 title 属性定位运输车辆牌号下拉框
            self.table_main_frame_content.get_by_title("运输车辆牌号").select_option(plate_number)

            logger.info(f"车牌号 {plate_number} 选择成功")

        except Exception as e:
            logger.error(f"错误：选择运输车辆牌号时发生异常 - {str(e)}")
            raise

    def select_carry_company(self, carry_company: str, license_plate: str):
        """
        选择承运单位并填写车牌号。

        :param carry_company: 承运单位名称，例如 "小王烟花托运公司"
        :param license_plate: 车牌号，例如 "湘A12345"
        """
        # 2. 点击“承运单位”输入框
        self.table_main_frame_content.get_by_role("textbox", name="承运单位").click()
        logger.info( "已点击 '承运单位'，打开选择弹窗。")
        table_main_frame.locator("iframe").nth(5).content_frame.get_by_role("row", name="单位名称：", exact=True).get_by_role("textbox").fill("小王烟花托运公司")
        table_main_frame.locator("iframe").nth(5).content_frame.get_by_role("button", name="查询").click()
        logger.info("已点击 '查询' 按钮。")
        time.sleep(1)
        # 2. 修正：用 XPath 1.0 语法定位目标 iframe（xMsgFrame + 3位数字）
        dynamic_iframe_locator = table_main_frame.locator(
            'xpath=//iframe[starts-with(@id, "xMsgFrame") and string-length(@id) = 12]'
        )


        # 3. 进入 iframe 内部
        inner_frame = dynamic_iframe_locator.nth(1).content_frame
        parent_tr = inner_frame.locator('tr[onDblClick="dblClick(this)"]')
        target_td = parent_tr.get_by_text(carry_company, exact=True)
        logger.info(f"查询结果已加载，找到单位名称 '{carry_company}'。")

        # 4. 确保元素可见并双击
        logger.info(f"等待单元格 '{carry_company}' 变为可见...")
        target_td.dblclick()
        logger.info(f"已成功选择单位名称为 '{carry_company}' 的行。")

        # 5. 选择车牌号
        table_main_frame.locator("#ysclcph").select_option(license_plate)
        logger.info(f"已成功选择车牌号为 '{license_plate}' 的行。")

    def add_driver(self, driver_name: str):
        """
        在指定的框架内选择驾驶员角色和姓名。
        (内部辅助函数)
        """
        logger.info("步骤 1/4: 选择驾驶员角色")
        self.table_main_frame_content.locator('//select[@name="lbtemp"]').scroll_into_view_if_needed()
        self.table_main_frame_content.locator('//select[@name="lbtemp"]').select_option(value="006")  # 006 对应驾驶员
        logger.info("已选择驾驶员角色")

        logger.info("步骤 2/4: 选择驾驶员姓名")
        self.table_main_frame_content.locator('//select[@name="xmtemp"]').select_option(label=driver_name)
        logger.info(f"已选择驾驶员姓名: {driver_name}")

    def click_add_button(self, button_text: str):
        """
        点击“+添加驾驶员/押运员”按钮。
        (内部辅助函数)
        """
        logger.info("步骤 3/4: 点击添加按钮")
        self.table_main_frame_content.get_by_role("button", name=button_text).click()
        #table_main_frame.get_by_role("button", name="+添加驾驶员/押运员").click()
        logger.info("已点击添加按钮")

    def add_escort(self,  escort_name: str):
        """
        在指定的框架内选择押运员角色和姓名。
        (内部辅助函数)
        """
        logger.info("步骤 3/4 (续): 选择押运员角色")
        role_select = self.table_main_frame_content.locator("#lbtemp2")
        role_select.select_option(value="007")  # 007 对应押运员
        logger.info("已选择押运员角色")

        logger.info("步骤 4/4: 选择押运员姓名")
        escort_name_select = table_main_frame.locator("#xmtemp2")

        logger.info(f"等待押运员姓名 '{escort_name}' 加载完成...")
        # 等待选项被添加到DOM中，这是一个很好的实践
        escort_name_option = escort_name_select.locator(f"option:has-text('{escort_name}')")
        escort_name_option.wait_for(state="attached", timeout=15000)
        logger.info(f"押运员姓名 '{escort_name}' 已加载。")

        escort_name_select.select_option(label=escort_name)
        logger.info(f"已选择押运员姓名: {escort_name}")

    def upload_critical_files(self, file_path: str = "123.jpg"):
        """
        上传所有关键文件，并通过检查对应 *BackImg 元素来验证上传是否成功。

        :param file_path: 要上传的文件路径。默认是 "123.jpg"。
        :return: 一个字典，包含每个文件的上传状态（成功/失败）和信息。
        """
        global table_main_frame
        files_to_upload = {
            "gxht": "烟花爆竹购销合同",
            "cpzljcbg": "烟花爆竹产品质量检测报告",
            "cpbzhgzm": "烟花爆竹产品包装合格证明",
            # "cydwyszzzm": "承运单位从事危险货物运输的资质证明",
            # "jsyyyyzgzm": "驾驶员押运员从事危险货物运输的资格",
            # "wxhwyszm": "危险货物运输车辆的道路运输证明"
        }

        if not os.path.exists(file_path):
            logger.error(f"要上传的文件 '{file_path}' 不存在！")
            return {name: {"success": False, "message": f"上传文件 '{file_path}' 不存在"} for name in
                    files_to_upload.values()}

        try:
            table_main_frame = get_table_main_frame_content(page)
        except Exception as e:
            logger.error(f"获取 table_main 框架失败: {e}")
            return {name: {"success": False, "message": f"无法获取页面框架: {e}"} for name in files_to_upload.values()}

        upload_results = {}
        logger.info("开始上传关键文件...")

        for field_id, field_name in files_to_upload.items():
            try:
                logger.info(f"--- 正在上传: {field_name} ---")

                upload_input = table_main_frame.locator(f"#{field_id}")
                upload_input.wait_for(state="attached", timeout=10000)

                # 滚动到元素以确保可点击
                upload_input.scroll_into_view_if_needed()

                # 执行上传操作
                upload_input.set_input_files(file_path)

                # 关键验证步骤：检查对应的 BackImg 元素是否存在
                # 我们等待它变得可见，超时时间设为5秒
                backimg_locator = table_main_frame.locator(f"#{field_id}BackImg")
                expect(backimg_locator).to_be_visible(timeout=5000)

                logger.info(f"'{field_name}' 上传成功。")
                upload_results[field_name] = {"success": True, "message": "上传成功，验证了 BackImg 元素存在。"}

            except Exception as e:
                error_message = f"'{field_name}' 上传失败: {e}"
                logger.error(error_message)
                upload_results[field_name] = {"success": False, "message": error_message}

        logger.info("所有文件上传操作已完成。")

        # 打印最终的上传结果摘要
        print("\n" + "=" * 50)
        print("文件上传结果摘要:")
        print("=" * 50)
        all_successful = True
        for name, result in upload_results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"{status}: {name}")
            if not result["success"]:
                print(f"   原因: {result['message']}")
                all_successful = False
        print("=" * 50)

        if all_successful:
            logger.info("所有关键文件均上传成功！")
        else:
            logger.error("部分文件上传失败，请检查日志。")

        return upload_results

    def submit_application(self):
        """
        提交申请表单，包含弹窗处理和提交结果验证。

        :return: 提交是否成功（bool）。
        """
        logger.info("开始执行提交操作...")

        # 1. 获取 table_main 框架（复用之前的框架获取函数）
        try:
            table_main_frame = get_table_main_frame_content(page)
        except Exception as e:
            logger.error(f"获取 table_main 框架失败：{str(e)}")
            return False

        # 2. 定位提交按钮并验证可点击状态
        submit_button = table_main_frame.get_by_role("button", name="提 交")

        # 3. 处理可能出现的弹窗（如确认提示）
        # 监听对话框事件，自动确认（根据实际情况调整：accept() 确认 / dismiss() 取消）
        dialog_handled = False

        def handle_dialog(dialog):
            nonlocal dialog_handled
            logger.info(f"发现弹窗：{dialog.type} - {dialog.message}")
            dialog.accept()  # 自动确认弹窗
            dialog_handled = True

        # 注册弹窗处理器（一次性监听）
        page.once("dialog", handle_dialog)

        # 4. 点击提交按钮
        try:
            submit_button.click()
            logger.info("提交按钮已点击，等待处理...")
        except Exception as e:
            logger.error(f"点击提交按钮失败：{str(e)}")
            return False

    def check_transport_permit_info(
            self,
            expected_sales_unit: str,
            expected_receive_unit: str,
            expected_carrier_unit: str,
            expected_apply_time: str = None,
            expected_status: str = None,
            expected_police_status: str = None
    ) -> bool:
        """
        检查表格中第二行的运输证信息是否符合预期。
        特别针对最新的HTML结构进行了优化，使用 use_inner_text 获取更准确的文本。

        :param self: 类实例的引用。
        :param expected_sales_unit: 预期销售单位 (必填)。
        :param expected_receive_unit: 预期收货单位 (必填)。
        :param expected_carrier_unit: 预期承运单位 (必填)。
        :param expected_apply_time: 预期申请时间（格式：YYYY-MM-DD），默认当天。
        :param expected_status: 预期状态（如：已提交）。
        :param expected_police_status: 预期公安审批状态（如：申请中）。
        :return: 所有检查项是否通过（bool）。
        """
        # 固定检查第二行，索引为1 (Playwright的locator.nth()从0开始计数)
        row_index = 1
        logger.info(f"--- 开始检查第 {row_index + 1} 行运输证信息 ---")

        def _clean_string(s: str) -> str:
            """内部辅助函数：清理字符串，移除所有非打印字符和多余空格。"""
            if not s:
                return ""
            cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B-\u200D\uFEFF\t\n\r]', '', s)
            cleaned = re.sub(r'[\s　]+', ' ', cleaned)
            return cleaned.strip()

        try:
            table_main_frame = get_table_main_frame_content(self.page)
        except Exception as e:
            logger.error(f"获取 table_main 框架失败：{e}")
            return False

        data_rows = table_main_frame.locator("tbody tr.list_table_rows_tr")

        if data_rows.count() <= row_index:
            logger.error(f"表格中数据行数不足（当前只有 {data_rows.count()} 行），无法检查第 {row_index + 1} 行。")
            return False

        current_row = data_rows.nth(row_index)

        FIELD_INDEXES = {
            "apply_time": 1,  # 申请时间（第2列）
            "sales_unit": 3,  # 销售单位（第4列）
            "receive_unit": 4,  # 收货单位（第5列）
            "carrier_unit": 5,  # 承运单位（第6列）
            "status": 8,  # 状态（第9列）
            "police_status": 10  # 公安审批状态（第11列）
        }

        if expected_apply_time is None:
            expected_apply_time = datetime.datetime.now().strftime("%Y-%m-%d")
            logger.info(f"未指定申请时间，默认验证当天：'{expected_apply_time}'")

        all_checks_passed = True
        check_results = []

        # --- 开始执行各项检查 ---

        # 1. 检查申请时间
        try:
            locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['apply_time'] + 1})")
            clean_expected = _clean_string(expected_apply_time)
            expect(locator).to_have_text(clean_expected, use_inner_text=True)
            check_results.append(f"✅ 申请时间：'{clean_expected}'（符合预期）")
        except Exception as e:
            actual_text = _clean_string(locator.text_content())
            check_results.append(
                f"❌ 申请时间：实际为 '{actual_text}'，预期为 '{_clean_string(expected_apply_time)}'。错误: {e}")
            all_checks_passed = False

        # 2. 检查销售单位
        try:
            locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['sales_unit'] + 1})")
            clean_expected = _clean_string(expected_sales_unit)
            expect(locator).to_have_text(clean_expected, use_inner_text=True)
            check_results.append(f"✅ 销售单位：'{clean_expected}'（符合预期）")
        except Exception as e:
            actual_text = _clean_string(locator.text_content())
            check_results.append(
                f"❌ 销售单位：实际为 '{actual_text}'，预期为 '{_clean_string(expected_sales_unit)}'。错误: {e}")
            all_checks_passed = False

        # 3. 检查收货单位
        try:
            locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['receive_unit'] + 1})")
            clean_expected = _clean_string(expected_receive_unit)
            expect(locator).to_have_text(clean_expected, use_inner_text=True)
            check_results.append(f"✅ 收货单位：'{clean_expected}'（符合预期）")
        except Exception as e:
            actual_text = _clean_string(locator.text_content())
            check_results.append(
                f"❌ 收货单位：实际为 '{actual_text}'，预期为 '{_clean_string(expected_receive_unit)}'。错误: {e}")
            all_checks_passed = False

        # 4. 检查承运单位
        try:
            locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['carrier_unit'] + 1})")
            clean_expected = _clean_string(expected_carrier_unit)
            expect(locator).to_have_text(clean_expected, use_inner_text=True)
            check_results.append(f"✅ 承运单位：'{clean_expected}'（符合预期）")
        except Exception as e:
            actual_text = _clean_string(locator.text_content())
            check_results.append(
                f"❌ 承运单位：实际为 '{actual_text}'，预期为 '{_clean_string(expected_carrier_unit)}'。错误: {e}")
            all_checks_passed = False

        # 5. 检查状态 (可选)
        if expected_status:
            try:
                locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['status'] + 1})")
                clean_expected = _clean_string(expected_status)
                expect(locator).to_have_text(clean_expected, use_inner_text=True)
                check_results.append(f"✅ 状态：'{clean_expected}'（符合预期）")
            except Exception as e:
                actual_text = _clean_string(locator.text_content())
                check_results.append(
                    f"❌ 状态：实际为 '{actual_text}'，预期为 '{_clean_string(expected_status)}'。错误: {e}")
                all_checks_passed = False

        # 6. 检查公安审批状态 (可选)
        if expected_police_status:
            try:
                locator = current_row.locator(f"td:nth-child({FIELD_INDEXES['police_status'] + 1})")
                clean_expected = _clean_string(expected_police_status)
                expect(locator).to_have_text(clean_expected, use_inner_text=True)
                check_results.append(f"✅ 公安审批状态：'{clean_expected}'（符合预期）")
            except Exception as e:
                actual_text = _clean_string(locator.text_content())
                check_results.append(
                    f"❌ 公安审批状态：实际为 '{actual_text}'，预期为 '{_clean_string(expected_police_status)}'。错误: {e}")
                all_checks_passed = False

        # --- 检查结果汇总 ---
        logger.info(f"\n第 {row_index + 1} 行运输证信息检查结果汇总：")
        for result in check_results:
            logger.info(result)

        if all_checks_passed:
            logger.info(f"✅ 第 {row_index + 1} 行所有检查项均通过！")
        else:
            logger.error(f"❌ 第 {row_index + 1} 行部分检查项未通过！")

        return all_checks_passed


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # 在旧版本 Playwright 中，忽略 HTTPS 错误的正确方式
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-javascript-breakpoints"]  # 关键参数：禁用 JS 断点
        )
        # browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)  # 在这里设置忽略 HTTPS 错误
        page = context.new_page()

        # 假设页面已经导航到目标URL
        page.goto("https://192.168.50.53:16443/yhbzglxt-qy/", timeout=10000)
        page.get_by_role("textbox", name="请输入加密锁密码").fill("1")
        page.get_by_role("link", name="登录").click()
        time.sleep(5)
        home_page = HomePage(page)
        home_page.navigate_to_page("许可证管理")


        license_page = licenseManagementPage(page)
        # license_page.select_import_export_status("配送")
        # license_page.select_redential_PSB("起运地县级公安机关")
        # time.sleep(1)
        # license_page.select_start_transport_time()
        # time.sleep(1)
        # license_page.select_end_transport_time()
        # license_page.trigger_search_popup("请选择零售单位")
        # license_page.fill_unit("ADW000000009863")
        #
        # license_page.add_delivered_goods(
        #     item_option="016--黑火药--/----#黑火药--黑火药--/--",
        #     product_specification="5",
        #     numbers_per_carton="10",
        #     carton_quantity="2"
        # )
        # license_page.select_carry_company("小王烟花托运公司","湘A66666")
        # license_page.add_driver_and_escort("王驾驶","王押运")
        # time.sleep(2)
        # license_page.upload_critical_files()
        # license_page.submit_application()
        # time.sleep(2)
        # license_page.check_transport_permit_info(
        #     expected_sales_unit="梁海斌烟花爆竹有限责任公司",
        #     expected_receive_unit="卢世微专用长期零售测试单位",
        #     expected_carrier_unit="小王烟花托运公司",
        #     expected_status="已提交",
        #     expected_police_status="申请中"
        # )

        transport_permit_type = "出口" #运输证类型
        sales_unit_name = "发大幅度答复批发企业1" #销售单位名称

        consigning_party_responsible_person_name = "张三丰" #托运负责人姓名
        consignor_responsible_person_phone = "13501374948" #托运负责人电话
        consignor_handler_name = "宋远桥" #托运经办人姓名
        consignor_handler_id_card = "110100198506020007" #托运经办人身份证
        consignor_handler_contact_phone = "18835934361" #托运经办人联系电话

        consignee_unit_name = "梁海斌烟花爆竹有限责任公司" #收货单位名称
        # consignee_address = "北京市海淀区京仪科技大厦" #收货地址
        # consignee_responsible_person_name = "俞莲舟" #收货负责人姓名
        # consignee_responsible_person_phone = "13801874046" #收货负责人电话

        carrier_unit_name = "重庆承运单位" #承运单位名称
        transport_vehicle_plate_number = "H5515" #运输车辆车牌号

        driver_name = "梁海斌" #驾驶员姓名
        escort_name = "是是是" #押运员姓名

        #出口
        time.sleep(1)
        license_page.select_import_export_status(transport_permit_type)
        license_page.trigger_search_popup("销售单位")
        license_page.query_fill_input(sales_unit_name)

        license_page.fill_consignor_info(consigning_party_responsible_person_name,
            consignor_responsible_person_phone,
            consignor_handler_name,
            consignor_handler_id_card,
            consignor_handler_contact_phone)
        # license_page.trigger_search_popup("购买单位名称")
        # license_page.query_fill_input(consignee_unit_name)
        license_page.trigger_search_popup("承运单位")
        license_page.query_fill_input(carrier_unit_name)
        license_page.select_transport_vehicle_plate(transport_vehicle_plate_number)
        license_page.add_driver(driver_name)
        # license_page.click_add_button("添 加")
        # license_page.add_escort(escort_name)
        # license_page.click_add_button("添 加")
        license_page.select_start_transport_time()
        license_page.select_end_transport_time()
        time.sleep(10)

