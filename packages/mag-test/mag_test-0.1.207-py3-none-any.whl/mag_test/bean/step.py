from typing import Optional

import allure
import pytest
from mag_tools.exception.app_exception import AppException
from mag_tools.log.logger import Logger
from mag_tools.model.common.message_type import MessageType
from mag_tools.utils.data.string_format import StringFormat
from mag_tools.utils.common.time_probe import TimeProbe

from mag_test.bean.base_test import BaseTest
from mag_test.bean.element_info import ElementInfo
from mag_test.core.app_driver import AppDriver
from mag_test.finder.element_finder import ElementFinder
from mag_test.model.control_type import ControlType
from mag_test.model.test_component_type import TestComponentType
from mag_test.model.usage_status import UsageStatus
from mag_test.utils.event_utils import EventUtils


class Step(BaseTest):
    def __init__(self, home_dir:str, name: Optional[str], control_name:Optional[str], control_type:Optional[ControlType],
                 automation_id:Optional[str], value:Optional[str], function_index:Optional[int]=None, step_index:Optional[int]=None,
                 parent_name:Optional[str]=None, parent_type:Optional[ControlType]=None,
                 pop_window:Optional[str]=None, status:UsageStatus=UsageStatus.NORMAL):
        super().__init__(home_dir, name, step_index, TestComponentType.STEP, None, status)

        self.__function_index = function_index
        self.__element_info = ElementInfo(control_type, control_name, automation_id, None,
                                          parent_name, parent_type, None,
                                          StringFormat.format(value), pop_window, home_dir)

    @pytest.mark.benchmark
    def start(self, driver:AppDriver, probe: TimeProbe):
        """
        启动测试步骤
        :param probe: 时间探针
        :param driver: AppDriver
        """
        if self._status == UsageStatus.NORMAL:
            super().start(driver, probe)

            with allure.step(f"  {self._index} {self._name}"):  # 描述测试步骤
                try:
                    Logger.debug(f'测试步骤[{self._name}]-{self._index}：\n\t{self.__element_info}')

                    if self.__element_info.is_virtual_control:
                        EventUtils.process_virtual(self.__element_info.main_type, self.__element_info.main_action, self.__element_info.value)
                    else:
                        # 查找控件并处理事件
                        ElementFinder.find(driver, self.__element_info)

                        # 检查消息提示框
                        alert_result = driver.check_alert()
                        if alert_result[0] in {MessageType.ERROR}:
                            raise AppException(alert_result[1])

                        # 如果指定了弹出窗口，则切换
                        if self.__element_info.pop_window:
                            driver = driver.switch_to_window_by_title(self.__element_info.pop_window)

                    self.success()
                except (AppException, Exception) as e:
                    Logger.error(f"测试步骤[{self._name}-{self._index}]失败: {self.__element_info.main_info}\n{str(e)}")
                    self.fail(str(e))

        return driver