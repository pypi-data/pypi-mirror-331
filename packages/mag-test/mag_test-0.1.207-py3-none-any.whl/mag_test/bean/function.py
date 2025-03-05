import json
import os

import allure
import pytest
from mag_tools.utils.common.time_probe import TimeProbe

from mag_test.bean.base_test import BaseTest
from mag_test.bean.step import Step
from mag_test.core.app_driver import AppDriver
from mag_test.model.control_type import ControlType
from mag_test.model.test_component_type import TestComponentType
from mag_test.model.usage_status import UsageStatus


class Function(BaseTest):
    def __init__(self, home_dir:str, plan_id:str, function_id:str, index:int, name:str, status:UsageStatus=UsageStatus.NORMAL):
        super().__init__(home_dir, name, index, TestComponentType.FUNCTION, None, status)
        self.__plan_id = plan_id
        self.__id = function_id  # 功能标识
        self.__steps = []

        self.__read()

    @pytest.mark.benchmark
    def start(self, driver:AppDriver, probe: TimeProbe)->AppDriver:
        """
        启动测试功能
        :param probe: 时间探针
        :param driver: AppDriver
        """
        if self._status == UsageStatus.NORMAL:
            with allure.step(f"{self._index} {self._name}"):  # 描述测试功能
                test_failed = False
                for step in self.__steps:
                    if test_failed:
                        step.skip()
                    else:
                        driver = step.start(driver, probe)
                        if step.is_fail():
                            self.fail('该功能测试失败')
                            test_failed = True
        return driver

    def __read(self):
        function_file = os.path.join(self.script_dir, self.__plan_id, f'{self.__id}.json')
        with open(function_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data['name']:
                self._name = data['name']
                self._status = UsageStatus[data['status']]

            for index, item in enumerate(data.get('steps', []), start=1):
                step = Step(home_dir=self._home_dir,
                            name=item.get('step_name', None),
                            control_name=item.get('control_name', None),
                            control_type=ControlType[item.get('control_type')] if item.get('control_type') else None,
                            automation_id=item.get('id', None),
                            value=item.get('value', None),
                            function_index=self._index,
                            step_index=index,
                            parent_name=item.get('parent', None),
                            parent_type=ControlType[item.get('parent_type')] if item.get('parent_type') else None,
                            pop_window=item.get('pop', None),
                            status=UsageStatus[item.get('status', None)])
                self.__steps.append(step)