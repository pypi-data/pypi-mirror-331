import ctypes
from ctypes import wintypes
from typing import Dict

from selenium.common.exceptions import InvalidSelectorException, NoSuchElementException, NoSuchWindowException, \
    TimeoutException, \
    WebDriverException

from mag_tools.log.logger import Logger
from mag_tools.model.log_type import LogType

# 定义回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

# 定义 Windows API 函数
EnumWindows = ctypes.windll.user32.EnumWindows
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowText = ctypes.windll.user32.GetWindowTextW
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow

class WindowFinder:
    # @staticmethod
    # def switch_to_window_by_title(driver: AppDriver, title: str):
    #     title = title.strip()
    #     if '.exe' in title.lower():
    #         driver = driver.new_driver(title)
    #     else:
    #         WindowFinder.__find_window_by_title(driver, title)
    #
    #     return driver

    # @staticmethod
    # def switch_to_window_by_title(driver: AppDriver, title: str):
    #     title = title.strip()
    #
    #     if '.exe' in title.lower():
    #         driver = driver.new_driver(title)
    #     else:
    #         hwnd = WebDriverWait(driver, 10).until(lambda drv: WindowFinder.find_window_by_title(title))
    #         ctypes.windll.user32.SetForegroundWindow(hwnd)
    #     return driver

    @staticmethod
    def find_window(title: str):
        hwnd_list = []

        def __enum_windows_proc(hwnd: wintypes.HWND, lParam: wintypes.LPARAM=None):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                window_title = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, window_title, length + 1)
                if title in window_title.value:
                    hwnd_list.append(hwnd)
            return True

        try:
            EnumWindows(EnumWindowsProc(__enum_windows_proc), 0)
            if hwnd_list is None or len(hwnd_list) == 0:
                raise NoSuchWindowException()

            return hwnd_list[0]
        except InvalidSelectorException as e:
            Logger.error(LogType.FRAME, f"查找窗口[{title}]选择器无效: {str(e)}")
        except NoSuchElementException as e:
            Logger.error(LogType.FRAME, f"查找窗口[{title}]出错: {str(e)}")
        except TimeoutException as e:
            Logger.error(LogType.FRAME, f"查找窗口[{title}]超时: {str(e)}")
        except WebDriverException as e:
            Logger.error(LogType.FRAME, f"查找窗口[{title}]时通讯异常: {str(e)}")
        except Exception as e:
            Logger.error(LogType.FRAME, f"未知异常：{str(e)}")



    # @staticmethod
    # def __find_window_by_title(driver: AppDriver, title: str):
    #     try:
    #         # 检查缓存中是否存在目标窗口的句柄
    #         if not driver.switch_to_window_by_title(title):
    #             initial_handles = driver.window_handles
    #             print(f"Initial handles: {initial_handles}")
    #
    #             WebDriverWait(driver, 20).until(lambda d: len(d.window_handles) > len(initial_handles))
    #
    #             windows = driver.window_handles
    #             print(f"All handles: {windows}")
    #             for window in windows:
    #                 driver.switch_to.window(window)
    #                 if title in driver.title:
    #                     break
    #     except NoSuchElementException as e:
    #         Logger.error(LogType.FRAME, f"查找窗口[{title}]出错: {str(e)}")
    #     except TimeoutException as e:
    #         Logger.error(LogType.FRAME, f"查找窗口[{title}]超时: {str(e)}")
    #     except WebDriverException as e:
    #         Logger.error(LogType.FRAME, f"查找窗口[{title}]时通讯异常: {str(e)}")
    #     except Exception as e:
    #         Logger.error(LogType.FRAME, f"未知异常：{str(e)}")

    @staticmethod
    def find_all_windows() -> Dict[str, int]:
        hwnd_map = {}

        def __enum_windows_proc(hwnd, lParam):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                window_title = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, window_title, length + 1)
                hwnd_map[window_title.value] = hwnd
            return True

        EnumWindows(EnumWindowsProc(__enum_windows_proc), 0)
        return hwnd_map