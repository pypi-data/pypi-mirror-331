from mag_tools.model.base_enum import BaseEnum


class MenuType(BaseEnum):
    DROP_DOWN = ("drop_down", "下拉菜单")
    POPUP = ("popup", "弹出菜单")
    CONTEXT = ("context", "上下文菜单")
    MENU_ITEM = ("menu_item", "菜单项")