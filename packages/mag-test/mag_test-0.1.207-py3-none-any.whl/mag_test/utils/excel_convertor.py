import os

import pandas as pd
from mag_tools.log.logger import Logger
from mag_tools.model.log_type import LogType
from mag_tools.utils.data.string_utils import StringUtils
from mag_tools.utils.file.excel_utils import ExcelUtils
from mag_tools.utils.file.json_file_utils import JsonFileUtils

from mag_test.model.control_type import ControlType
from mag_test.model.usage_status import UsageStatus


class ExcelConvertor:
    def __init__(self, home_dir: str):
        self.__home_dir = home_dir

    def convert(self, plan_excel_file:str, test_type:str, sheet_name:str):
        excel_file = self.__get_excel_file(plan_excel_file)

        plan_id = self.__convert_plan(excel_file, test_type, sheet_name)
        self.__convert_function(excel_file, plan_id)

        Logger.info(LogType.FRAME, "将Excel格式的测试计划转换为JSon脚本完毕", True)

        return plan_id

    def __convert_plan(self, excel_file:str, test_type:str, sheet_name:str):
        keywords = "单元测试" if test_type.upper() == "UNIT" else "测试计划"
        df = pd.read_excel(excel_file, sheet_name)  # 读取 Excel 文件
        df = ExcelUtils.clear_empty(df) # 清除空白的行与列

        title = ExcelUtils.get_first_cell_of_row_by_keyword(df, 0, keywords)
        plan_name, plan_id = StringUtils.split_name_id(title)
        if not plan_id:
            plan_id = StringUtils.pick_head(plan_name, sheet_name) if test_type.upper() == "ALL" else "unit"

        df.columns = df.iloc[1]  # 将第1行设置为列名
        df = df.drop(index=range(2)).reset_index(drop=True) # 删除第1行及其之前的所有行

        # 按模块分组
        df["功能模块"] = df["功能模块"].ffill()
        df["测试用例"] = df["测试用例"].ffill()
        df["备注"] = df["备注"].ffill()

        if "用例状态" in df.columns:
            df["用例状态"] = df["用例状态"].ffill()

        module_groups = df.groupby("功能模块", sort=False)

        _modules = []
        for _module_name, module_group in module_groups:
            Logger.debug(LogType.FRAME, f"功能模块名：{_module_name}")

            _cases = []
            case_groups = module_group.groupby("测试用例", sort=False)
            for _case_name, case_group in case_groups:
                Logger.debug(LogType.FRAME, f"测试用例名：{_case_name}")

                _case_desc = ExcelUtils.get_value_from_group(case_group, "备注")
                _case_status = UsageStatus.of_desc(ExcelUtils.get_value_from_group(case_group, "用例状态", "正常"))

                _functions = []
                function_groups = case_group.groupby("功能", sort=False)
                for _function_name, function_group in function_groups:
                    _function_name, _function_id = StringUtils.split_name_id(str(_function_name))
                    # 功能标识为空时忽略
                    if _function_id:
                        _functions.append({"id": _function_id, "name": _function_name})

                _case = {"name": _case_name, "desc": _case_desc, "functions": _functions, "status": _case_status}
                _cases.append(_case)
            _module = {"name": _module_name, "cases": _cases}
            _modules.append(_module)

        _plan = {"name": plan_name, "modules": _modules}

        JsonFileUtils.save_as_json(self.__get_plan_file(plan_id), _plan)

        return plan_id

    def __convert_function(self, excel_file, plan_id):
        df = pd.read_excel(excel_file, "功能")  # 读取 Excel 文件
        df = ExcelUtils.clear_empty(df) # 清除空白的行与列
        df = ExcelUtils.delete_row_with_keyword(df, 0, '测试功能')

        df.columns = df.iloc[0]  # 将第1行设置为列名
        df = df.drop(index=range(1)).reset_index(drop=True) # 删除第0行及其之前的所有行

        # 按模块分组
        df["功能"] = df["功能"].ffill()
        if "功能状态" in df.columns:
            df["功能状态"] = df["功能状态"].ffill()
        function_groups = df.groupby("功能", sort=False)

        for _function_name, function_group in function_groups:
            Logger.debug(LogType.FRAME, f"功能：{_function_name}")
            _function_status = UsageStatus.of_desc(ExcelUtils.get_value_from_group(function_group, "功能状态", "正常"))

            test_steps = []
            step_groups = function_group.groupby("步骤", sort=False)
            for step_name, step_group in step_groups:
                Logger.debug(LogType.FRAME, f"功能步骤：{step_name}")

                _element_name = ExcelUtils.get_value_from_group(step_group, "控件名")
                _element_type = ControlType.of_desc(ExcelUtils.get_value_from_group(step_group, "控件类型"))
                _element_id = ExcelUtils.get_value_from_group(step_group, "控件标识")
                _element_parent_name = ExcelUtils.get_value_from_group(step_group, "父控件名")
                _element_parent_type = ControlType.of_desc(ExcelUtils.get_value_from_group(step_group, "父控件类型"))
                _element_value = ExcelUtils.get_value_from_group(step_group, "输入")
                _element_pop = ExcelUtils.get_value_from_group(step_group, "弹窗")
                _element_status = UsageStatus.of_desc(ExcelUtils.get_value_from_group(step_group, "步骤状态", "正常"))

                test_step = {"control_name": str(_element_name) if _element_name else None,
                            "control_type": _element_type.name if _element_type else None,
                            "id": str(_element_id) if _element_id else None,
                            "parent": str(_element_parent_name) if _element_parent_name else None,
                            "parent_type": _element_parent_type.name if _element_parent_type else None,
                            "value": str(_element_value) if _element_value else None,
                            "step_name": str(step_name) if step_name else None,
                            "pop": str(_element_pop) if _element_pop else None,
                            "status": _element_status}
                test_steps.append(test_step)

            _function_name, _function_id = StringUtils.split_name_id(str(_function_name))
            _function = {"name": _function_name, "steps": test_steps, "status": _function_status}

            # 功能标识为空时忽略
            if _function_id:
                JsonFileUtils.save_as_json(self.__get_function_file(plan_id, _function_id), _function)

    def __get_excel_file(self, excel_file):
        if ":" not in excel_file:
            excel_dir = os.path.join(self.__home_dir, 'excel')
            excel_file = os.path.join(excel_dir, excel_file)
        return excel_file

    def __get_plan_file(self, plan_id):
        script_dir = os.path.join(self.__home_dir, 'script')
        return os.path.join(script_dir, plan_id, 'plan.json')

    def __get_function_file(self, plan_id, function_name):
        script_dir = os.path.join(self.__home_dir, 'script')
        return os.path.join(script_dir, plan_id, f'{function_name}.json')
