from mag_tools.model.base_enum import BaseEnum


class InitStatus(BaseEnum):
    T = ("T", "表格转置")
    EXPANDED = ("expanded", "树节点展开")
    SELECTED = ("selected", "选中")