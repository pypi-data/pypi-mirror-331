from typing import Optional

from mag_tools.utils.data.string_utils import StringUtils
from mag_tools.model.base_enum import BaseEnum


class ControlType(BaseEnum):
    """
    控件类型枚举
    枚举值为不包含前缀的控件类型名，如：ControlType.EDIT
    """

    EDIT = ('Edit', '文本框', None)  # TextBox
    DOC = ('Document', '文档', None)  # Document
    BUTTON = ('Button', '按钮', None)  # Button
    SPLIT_BUTTON = ('SplitButton', '拆分按钮', None)  # SplitButton
    CHECKBOX = ('CheckBox', '复选框', None)  # CheckBox
    RADIO = ('RadioButton', '单选按钮', None)  # RadioButton
    MENU_BAR = ('MenuBar', '菜单栏', None)  # MenuBar
    MENU = ('Menu', '菜单', 'MenuItem')  # Menu
    MENU_ITEM = ('MenuItem', '菜单项', None)  # MenuItem
    CONTEXT_MENU = ('ContextMenu', '上下文菜单', None)  # ContextMenu
    WINDOW = ('Window', '主窗口', None)  # Main Window
    DIALOG = ('Dialog', '对话框', None)  # Dialog
    MESSAGE = ('MessageBox', '消息框', None)  # MessageBox
    LABEL = ('Text', '标签', None)  # Label
    LIST = ('List', '列表框', 'ListItem')  # ListBox
    LIST_VIEW = ('ListView', '列表视图', 'ListItem')  # ListView
    LIST_ITEM = ('ListItem', '列表项', None)  # ListBox/ListView包含ListItem
    COMBO_BOX = ('ComboBox', '组合框', None)  # ComboBox
    TREE = ('Tree', '树视图', 'TreeItem')  # TreeView
    TREE_ITEM = ('TreeItem', '树节点', None)  # TreeItem
    TABLE = ('Table', '表格', 'DataItem')    # Table
    TABLE_ROW = ('TableRow', '表格行', None) # TableRow
    DATA_ITEM = ('DataItem', '数据项', None) # DataItem
    TAB = ('Tab', '选项卡', 'TabItem')  # TabControl
    TAB_ITEM = ('TabItem', 'TAB项', None)  # Tab项
    GROUP_TAB = ('GroupTab', 'Tab组', None)  # 组TabItem
    DATETIME = ('SysDateTimePick32', '日期时间', None)  # 类名为 SysDateTimePick32
    PROGRESS = ('ProgressBar', '进度条', None)  # ProgressBar
    TITLE = ('TitleBar', '标题栏', None)  # TitleBar
    SLIDER = ('Slider', '滑块', None)  # Slider
    STATUS = ('StatusBar', '状态条', None)  # StatusBar
    TOOL = ('ToolBar', '工具栏', None)  # ToolBar
    GROUP = ('Group', '分组', None)  # 组Group
    PANEL = ('Panel', 'PANEL', None)  # Panel 分组和布局
    PANE = ('Pane', 'PANE', None)  # Panel 分组框或面板
    HEADER = ('Header', '表格标题', None)  # Header
    FILE = ('File', '文件', None) # 文件操作，虚拟控件
    ALL = ('*', '全部', None) # 全部控件

    def __init__(self, code: str, desc: str, child: Optional[str] = None):
        super().__init__(code, desc)
        self.__child = child

    @property
    def child(self):
        return ControlType.of_code(self.__child)

    @classmethod
    def get_by_element(cls, element):
        if element is None:
            return None

        type_name = StringUtils.pick_tail(element.tag_name, ".")
        return cls.of_code(type_name)

    @property
    def is_virtual(self) -> bool:
        """
        判定是否为虚拟控件
        """
        return self in {ControlType.FILE}
