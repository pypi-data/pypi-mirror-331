import json
import os

import pytest
from mag_tools.log.logger import Logger
from mag_tools.model.log_type import LogType
from mag_tools.utils.common.time_probe import TimeProbe

from mag_test.bean.base_test import BaseTest
from mag_test.bean.module import Module
from mag_test.core.app_driver import AppDriver
from mag_test.model.test_component_type import TestComponentType


class Plan(BaseTest):
    def __init__(self, home_dir:str, plan_id:str):
        super().__init__(home_dir, '', None, TestComponentType.PLAN, None, None)
        self.__id = plan_id  # 测试计划标识

        self.__read()

    @pytest.mark.benchmark
    def start(self, driver: AppDriver, probe: TimeProbe):
        super().start(driver, probe)

        for module in self.__modules:
            driver = module.start(driver, probe)

        return driver

    def title(self):
        return self._name

    def __read(self):
        self.__modules = []

        plan_file = os.path.join(self.script_dir, self.__id, 'plan.json')
        with open(plan_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self._name = data.get('name', '')

            for index, item in enumerate(data.get('modules'), start=1):
                if isinstance(item, dict):
                    module = Module.from_map(self._home_dir, self.__id, index, item)
                    self.__modules.append(module)
                else:
                    Logger.error(LogType.FRAME, f"Invalid module data at index {index}: {item}")