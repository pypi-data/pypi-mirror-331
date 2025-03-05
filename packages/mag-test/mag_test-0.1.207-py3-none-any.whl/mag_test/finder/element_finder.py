from typing import Optional

from mag_tools.log.logger import Logger
from mag_tools.model.log_type import LogType
from mag_tools.utils.common.time_probe import TimeProbe
from selenium.common.exceptions import InvalidSelectorException, NoSuchElementException, TimeoutException, \
    WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from mag_test.bean.control import Control
from mag_test.bean.element_info import ElementInfo
from mag_test.core.app_driver import AppDriver
from mag_test.finder.driver_finder_utils import DriverFinderUtils
from mag_test.finder.element_finder_utils import ElementFinderUtils
from mag_test.model.control_type import ControlType
from mag_test.utils.event_utils import EventUtils
from mag_test.utils.tree_utils import TreeUtils
from mag_test.model.init_status import InitStatus
from mag_test.model.menu_type import MenuType
from mag_test.utils.element_utils import ElementUtils


class ElementFinder:
    @staticmethod
    def find(driver:AppDriver, element_info: ElementInfo):
        Logger.debug(f'开始查找控件：{element_info.main_info}')
        probe = TimeProbe.get_probe('查找控件')

        # 菜单
        if element_info.main_type == ControlType.MENU:
            ElementFinder.__find_menu(driver, element_info)
        # 窗口
        elif element_info.main_type == ControlType.WINDOW:
            ElementFinder.__find_window(driver, element_info)
        # 日期时间
        elif element_info.main_type == ControlType.DATETIME:
            ElementFinder.__find_datetime(driver, element_info)
        else:
            # 查找父控件并处理响应事件
            parent = ElementFinder.__find_parent(driver, element_info.parent_info, probe)

            # 查找主控件并处理响应事件
            main_element = ElementFinder.__find_main_element(driver, parent, element_info.main_info, element_info.value, probe)

            # 查找子控件并处理响应事件
            child_element = ElementFinder.__find_child_element(driver, main_element, element_info.child_info, element_info.value, probe)

            # 查找弹出菜单并处理响应事件
            ElementFinder.__find_context_menu(driver, child_element, element_info.pop_menu, probe)

        probe.write_log()

    @staticmethod
    def __find_menu(driver:AppDriver, element_info:ElementInfo):
        """
        查找菜单控件
        参数：
        name 菜单及菜单项名，格式：菜单项名/子菜单项名/...
        parent_name 父控件名
        parent_control_type 父控件类型
        """
        items = element_info.menu_items

        element = None
        actions = ActionChains(driver)

        for index, item in enumerate(items):
            element = DriverFinderUtils.find_element_by_type_wait(driver, item, ControlType.MENU_ITEM)
            if index < len(items) - 1:
                actions.move_to_element(element).click().perform()
        return element

    @staticmethod
    def __find_datetime(driver:AppDriver, element_info:ElementInfo):
        """
        查找日期时间控件
        参数：
        name 日期时间控件名
        """
        parent = ElementFinder.__find_parent(driver, element_info.parent_info)
        if parent:
            dt = ElementFinderUtils.find_element_by_class(parent, element_info.main_name, 'SysDateTimePick32')
        else:
            dt = DriverFinderUtils.find_element_by_class(driver, element_info.main_name, 'SysDateTimePick32')

        return dt

    @staticmethod
    def __find_window(driver:AppDriver, element_info: ElementInfo):
        """
        查找窗口
        参数：
        name 窗口名（关键词）
        """
        return driver.find_element(By.XPATH, f"//Window[contains(@Name, '{element_info.main_name}')]")
    
    @staticmethod
    def __find_context_menu(driver:AppDriver, element: WebElement, menu_Info: Optional[Control], probe: Optional[TimeProbe]=None):
        if menu_Info and menu_Info.menu_type:
            probe.check('查找菜单')

            try:
                menu = None
                actions = ActionChains(driver)

                menu_item = None
                if menu_Info.menu_type == MenuType.MENU_ITEM:
                    element.click()

                    if menu_Info.automation_id:
                        menu_item = DriverFinderUtils.find_element_by_automation(driver, menu_Info.automation_id)
                    else:
                        menu_item = DriverFinderUtils.find_element_by_type(driver, menu_Info.name, ControlType.MENU_ITEM)
                else:
                    if menu_Info.menu_type == MenuType.CONTEXT:
                        actions.move_to_element(element).context_click(element).perform()
                        menu = DriverFinderUtils.find_element_by_class(driver.root_driver, '上下文', '#32768')
                    elif menu_Info.menu_type == MenuType.POPUP:
                        actions.move_to_element(element).click(element).perform()
                        menu = DriverFinderUtils.find_element_by_type(driver, '弹出窗口', ControlType.WINDOW)

                    if menu:
                        if menu_Info.automation_id:
                            menu_item = ElementFinderUtils.find_element_by_automation(menu, menu_Info.automation_id)
                        else:
                            menu_item = ElementFinderUtils.find_element_by_type(menu, menu_Info.name, ControlType.MENU_ITEM)

                        Logger.debug(LogType.FRAME, f"控件的菜单类型为：{menu_Info.menu_type.desc}")

                if menu_item:
                    menu_item.click()
                    Logger.debug(f'查找菜单完毕：{menu_Info}')
            except (NoSuchElementException, InvalidSelectorException, WebDriverException) as e :
                Logger.throw(f"未找到菜单：{str(e)}")

    @staticmethod
    def __find_child_element(driver: AppDriver, main_element: WebElement, child_info: Control, value: Optional[str] = None, probe: Optional[TimeProbe]=None):
        """
        查找树视图
        参数：
        name 树视图名，格式：树视图名/树节点名/菜单名，树视图名和菜单名可为空，只支持菜单模式的弹出菜单
        """
        if child_info:
            probe.check('查找子控件')

            if child_info.action == InitStatus.EXPANDED:
                TreeUtils.expand_all(driver, main_element)

            if child_info.automation_id:
                element = ElementFinderUtils.find_element_by_automation(main_element, child_info.automation_id)
            else:
                element = ElementFinderUtils.find_element_by_type(main_element, child_info.name, child_info.control_type)

            EventUtils.process_final_element(driver, element, child_info, value)

            Logger.debug(f'查找子控件完毕：{child_info}')
        else:
            element = main_element

        return element

    @staticmethod
    def __find_main_element(driver: AppDriver, parent: WebElement, main_info: Control, value: Optional[str] = None, probe: Optional[TimeProbe]=None) -> WebElement:
        try:
            if main_info.automation_id:
                probe.check('查找主控件')

                if parent:
                    element = ElementFinderUtils.find_element_by_automation(parent, main_info.automation_id)
                else:
                    element = DriverFinderUtils.find_element_by_automation_wait(driver, main_info.automation_id)
            else:
                if parent:
                    element = ElementFinderUtils.find_element_by_type(parent, main_info.name, main_info.control_type)
                else:
                    element = DriverFinderUtils.find_element_by_type_wait(driver, main_info.name, main_info.control_type)

            if main_info.is_composite:
                offset = ElementUtils.get_main_offset(value, element)
                EventUtils.click_offset(driver, element, offset)
            else:
                EventUtils.process_final_element(driver, element, main_info, value)

            Logger.debug(f'查找主控件完毕：{main_info}')
            return element
        except NoSuchElementException as e:
            Logger.throw(f'未找到主控件：{str(e)}')    # 模糊查找控件时，返回None正常
        except InvalidSelectorException as e:
            Logger.throw(f'无效的控件选项：{str(e)}')  # 模糊查找控件时，返回None正常
        except TimeoutException as e:
            Logger.throw(f'连接失败：{str(e)}')  # 模糊查找控件时，返回None正常
        except WebDriverException as e:
            Logger.throw(f'连接失败或超时：{str(e)}')   # 模糊查找控件时，返回None正常

    @staticmethod
    def __find_parent(driver:AppDriver, parent_info: Control, probe: Optional[TimeProbe]=None) -> WebElement:
        parent = None
        if parent_info:
            try:
                probe.check('查找父控件')

                if parent_info.automation_id:
                    parent = DriverFinderUtils.find_element_by_automation_wait(driver, parent_info.automation_id)
                elif parent_info.control_type:
                    parent = DriverFinderUtils.find_element_by_type_wait(driver, parent_info.name, parent_info.control_type)
            except (NoSuchElementException, InvalidSelectorException, WebDriverException) as e:
                Logger.throw(f'查找父控件失败：{parent_info}\n{str(e)}')

        Logger.debug(f'查找父控件完毕：{parent_info}')
        return parent