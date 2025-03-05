import os
from typing import Optional

from mag_tools.log.logger import Logger
from mag_tools.model.log_type import LogType
from mag_tools.utils.common.time_probe import TimeProbe

from mag_test.model.test_component_type import TestComponentType
from mag_test.model.test_result import TestResult
from mag_test.model.usage_status import UsageStatus


class BaseTest:
    def __init__(self, home_dir, name:str, index:Optional[int]=None, test_component_type:Optional[TestComponentType] = None,
                 description:Optional[str]=None, status:Optional[UsageStatus]=UsageStatus.NORMAL):
        self._name = name
        self._index = index
        self._test_component_type = test_component_type
        self._description = description
        self._test_result = TestResult.SKIP
        self._err_message = None
        self._home_dir = home_dir
        self._status = status if status else UsageStatus.NORMAL

    def start(self, driver, probe: TimeProbe):
        probe.check(f"{self._test_component_type.desc}[{self._name}]")
        Logger.info(LogType.FRAME, f"执行{self._test_component_type.desc}({self._name})完毕")

    def skip(self):
        Logger.info(f"{self._test_component_type.desc}-{self._name}未测试")

    def fail(self, message:Optional[str]=''):
        self._test_result = TestResult.FAIL
        self._err_message = message
        Logger.error(f"{self._test_component_type.desc}-{self._name}失败：{message}")
        assert False

    def success(self):
        self._test_result = TestResult.SUCCESS
        Logger.info(f"{self._test_component_type.desc}-{self._name}成功")

    def is_success(self):
        return self._test_result == TestResult.SUCCESS

    def is_fail(self):
        return self._test_result == TestResult.FAIL

    @property
    def script_dir(self):
        return os.path.join(self._home_dir, 'script')

    # def get_attachment(self, attachment_name):
    #     attachment_dir = os.path.join(self._home_dir, 'attachment')
    #     return os.path.join(attachment_dir, attachment_name) if attachment_name else None