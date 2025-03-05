import os
from typing import Any, Optional

from mag_tools.utils.data.string_utils import StringUtils

from mag_test.bean.control import Control
from mag_test.model.control_type import ControlType
from mag_test.model.action_type import ActionType
from mag_test.model.menu_type import MenuType


class ElementInfo:
    """
    控件信息，用于查询条件
    """
    def __init__(self, element_type:ControlType, name_path:Optional[str]=None, id_path:Optional[str]=None,
                 class_name:Optional[str]=None, parent_name_id:Optional[str] = None,parent_type:Optional[ControlType]=None,
                 parent_class:Optional[str]=None, value:Optional[Any]=None,
                 pop_window:Optional[str]=None, home_dir:Optional[str]=None,):
        """
        控件信息，用于查询条件
        :param name_path: 控件名和ID路径，格式：主控件名或ID{动作}/子控件名或ID{动作}/菜单项名或ID{动作}
        :param id_path: 控件标识路径，格式：主控件ID{动作}/子控件ID{动作}/菜单项ID{动作}
        :param element_type: 控件类型,不能为空
        :param class_name: 控件类名
        :param parent_name_id: 父控件名或ID，父控件通常为容器
        :param parent_type: 父控件类型
        :param parent_class: 父控件类名
        """
        self.__main_element = Control(control_type=element_type, class_name=class_name)
        self.__parent: Optional[Control] = None
        self.__child: Optional[Control] = None
        self.pop_menu: Optional[Control] = None
        self.__home_dir = home_dir

        if parent_name_id or parent_type or parent_class:
            parent_name = parent_name_id if parent_name_id and not parent_name_id.isdigit() else None
            parent_id = parent_name_id if parent_name_id and parent_name_id.isdigit() else None
            self.__parent = Control(name=parent_name, automation_id=parent_id, control_type=parent_type, class_name=parent_class)

        self.value = value
        if value and self.main_type == ControlType.TABLE and '.json' in value:
            self.value = os.path.join(os.path.join(self.__home_dir, 'attachment'), value)

        self.pop_window = pop_window

        if element_type == ControlType.MENU:
            self.menu_items = name_path.split('/') if name_path else id_path.split('/') if id_path else []
        else:
            self.__parse_name_id_path(name_path)
            self.__parse_id_path(id_path)

    @property
    def main_info(self):
        return self.__main_element

    @property
    def main_name(self):
        return self.__main_element.name

    @property
    def main_id(self):
        return self.__main_element.automation_id

    @property
    def main_type(self):
        return self.__main_element.control_type

    @property
    def main_action(self):
        return self.__main_element.action

    @property
    def init_status(self):
        return

    @property
    def parent_info(self):
        return self.__parent

    @property
    def parent_name(self):
        return self.__parent.name if self.__parent else None

    @property
    def parent_id(self):
        return self.__parent.automation_id if self.__parent else None

    @property
    def parent_type(self):
        return self.__parent.control_type if self.__parent else None

    @property
    def child_info(self):
        return self.__child

    @property
    def child_name(self):
        return self.__child.name if self.__child else None

    @property
    def child_id(self):
        return self.__child.automation_id if self.__child else None

    @property
    def child_type(self):
        return ControlType.of_code(self.__main_element.control_type.child) if self.__child else None

    @property
    def child_action(self):
        return self.__child.action if self.__child else None

    @property
    def is_virtual_control(self) -> bool:
        return self.__main_element.control_type.is_virtual

    def __str__(self) -> str:
        attributes = {k: v for k, v in self.__dict__.items() if v is not None}
        return f"ElementInfo({', '.join(f'{k}={v}' for k, v in attributes.items())})"

    def __parse_name_id_path(self, name_path:Optional[str]) -> None:
        """
        解析名字/ID路径
        :param name_path: 控件名和ID路径，格式：主控件名或ID{动作}/子控件名或ID{动作}/菜单项名或ID{动作}
        """
        if name_path:
            if name_path.count('/') == 2:
                main_item, child_item, menu_item = tuple(name_path.split('/'))

                # 解析主控件
                main_name, main_id, main_action, main_init_status = Control.parse_name_id_path(main_item, control_type=self.__main_element.control_type)
                self.__main_element.name = main_name
                self.__main_element.automation_id = main_id
                self.__main_element.action = main_action
                self.__main_element.init_status = main_init_status
                self.__main_element.is_composite = True

                # 解析子控件
                if child_item:
                    child_type = self.main_type.child
                    child_name, child_id, child_action, _ = Control.parse_name_id_path(child_item, control_type=child_type)

                    # 当子控件动作为空且其为最终控件时，设置缺省CLICK动作
                    if child_action is None and not menu_item:
                        child_action = ActionType.CLICK
                    self.__child = Control(child_name, control_type=child_type, automation_id=child_id, action=child_action)

                # 解析菜单控件
                if menu_item:
                    menu_item_name_id, menu_type_str, _ = StringUtils.split_by_keyword(menu_item, '{}')
                    menu_item_name = menu_item_name_id if menu_item_name_id and not menu_item_name_id.isdigit() else None
                    menu_item_id = menu_item_name_id if menu_item_name_id and menu_item_name_id.isdigit() else None

                    menu_type = MenuType.of_code(menu_type_str) if menu_type_str else MenuType.CONTEXT
                    self.pop_menu = Control(menu_item_name, automation_id=menu_item_id, menu_type=menu_type)
            elif '/' not in name_path:
                main_name, main_id, main_action, main_init_status = Control.parse_name_id_path(name_path, control_type=self.__main_element.control_type)
                self.__main_element.name = main_name
                self.__main_element.automation_id = main_id
                self.__main_element.action = main_action
                self.__main_element.init_status = main_init_status

    def __parse_id_path(self, id_path:Optional[str]) -> None:
        """
        解析ID路径
        :param id_path: 控件ID路径，格式：主控件ID{动作}/子控件ID{动作}/菜单项ID{动作}
        """
        if id_path:
            if id_path.count('/') == 2:
                main_item, child_item, menu_item = tuple(id_path.split('/'))

                # 解析主控件
                main_id, main_action, main_init_status = Control.parse_id_path(main_item, control_type=self.__main_element.control_type)
                self.__main_element.automation_id = main_id
                self.__main_element.action = main_action
                self.__main_element.init_status = main_init_status
                self.__main_element.is_composite = True

                # 解析子控件
                if child_item:
                    child_type = self.main_type.child
                    child_id, child_action, _ = Control.parse_id_path(child_item, control_type=child_type)

                    # 当子控件动作为空且其为最终控件时，设置缺省CLICK动作
                    if child_action is None and not menu_item:
                        child_action = ActionType.CLICK
                    self.__child = Control(control_type=child_type, automation_id=child_id, action=child_action)

                # 解析菜单控件
                if menu_item:
                    menu_item_id, menu_type_str, _ = StringUtils.split_by_keyword(menu_item, '{}')

                    menu_type = MenuType.of_code(menu_type_str) if menu_type_str else MenuType.CONTEXT
                    self.pop_menu = Control(automation_id=menu_item_id, menu_type=menu_type)
            elif '/' not in id_path:
                main_id, main_action, main_init_status = Control.parse_id_path(id_path, control_type=self.__main_element.control_type)
                self.__main_element.automation_id = main_id
                self.__main_element.action = main_action
                self.__main_element.init_status = main_init_status
