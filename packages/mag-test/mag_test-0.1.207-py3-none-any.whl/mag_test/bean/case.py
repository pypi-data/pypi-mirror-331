from typing import Any, Dict, List

import allure
import pytest
from mag_tools.utils.common.time_probe import TimeProbe

from mag_test.bean.base_test import BaseTest
from mag_test.bean.function import Function
from mag_test.core.app_driver import AppDriver
from mag_test.model.test_component_type import TestComponentType
from mag_test.model.usage_status import UsageStatus


class Case(BaseTest):
    def __init__(self, home_dir:str, plan_id:str, name:str, description:str, functions:List[Function],
                 index:int, status:UsageStatus=UsageStatus.NORMAL):
        super().__init__(home_dir, name, index, TestComponentType.CASE, description, status)
        self.__plan_id = plan_id
        self.__functions = functions

    @pytest.mark.benchmark
    def start(self, driver:AppDriver, probe: TimeProbe):
        if self._status == UsageStatus.NORMAL:
            super().start(driver, probe)

            allure.dynamic.story(self._name)  # 测试用例名（标题）

            test_failed = False
            for function in self.__functions:
                if test_failed:
                    function.skip()
                else:
                    driver = function.start(driver, probe)
                    if function.is_fail():
                        self.fail('该用例测试失败')
                        test_failed = True

        return driver

    def append(self, function:Function):
        self.__functions.append(function)

    @staticmethod
    def from_map(home_dir:str, plan_id:str, index:int, data:Dict[str, Any]):
        name = data.get('name')
        description = data.get('desc')
        status = UsageStatus[data.get('status')]

        case = Case(home_dir, plan_id, name, description, [], index, status)

        for function_index, function_item in enumerate(data.get('functions'), start=1):
            function_id = function_item.get('id')
            function_name = function_item.get('name', '')

            function = Function(home_dir, plan_id, function_id, index, function_name)
            case.append(function)

        return case