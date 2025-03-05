from typing import Optional

from mag_tools.model.base_enum import BaseEnum

from mag_test.model.control_type import ControlType


class ActionType(BaseEnum):
    CLICK = ("click", "单击")   # 按钮、菜单、ITEM等控件的缺省操作
    DOUBLE_CLICK = ("double_click", "双击")
    RIGHT_CLICK = ("right_click", "右键单击")
    CLEAR = ("clear", "清除")
    SUBMIT = ("submit", "提交")
    SEND_KEYS = ("send_keys", "发送按键")
    # 以下为虚拟或组合的控件事件
    SET_TEXT = ("set_text", "设置文件")  # 文本框、文档等可编辑控件的缺省操作，相当于 CLEAR和SEND_KEYS
    SELECT = ("select", "选择")   #  # 应用于可选择控件
    CLEAR_DIR = ("clear_dir", "清除目录") # 应用于目录操作
    DELETE_DIR = ("delete_dir", "删除目录")  # 应用于目录操作
    DELETE_FILE = ("delete_file", "删除文件") # 应用于文件操作
    MENU_ITEM = ("menu_item", "点击菜单项") # 为缺省操作

    @classmethod
    def default_action(cls, control_type:Optional[ControlType]):
        _default_action = cls.CLICK
        if control_type in {ControlType.EDIT, ControlType.DOC, ControlType.COMBO_BOX}:
            _default_action = cls.SET_TEXT

        return _default_action