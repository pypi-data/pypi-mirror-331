from typing import Optional

from mag_tools.utils.data.string_utils import StringUtils

from mag_test.model.action_type import ActionType
from mag_test.model.control_type import ControlType
from mag_test.model.menu_type import MenuType
from mag_test.model.init_status import InitStatus


class Control:
    def __init__(self, name: Optional[str] = None, control_type: Optional[ControlType] = None, automation_id: Optional[str] = None,
                 action: Optional[ActionType] = None, class_name: Optional[str] = None,
                 menu_type: Optional[MenuType] = None, init_status: Optional[InitStatus] = None, is_composite: bool = False):
        self.name = name
        self.control_type = control_type
        self.automation_id = automation_id
        self.action = action
        self.menu_type = menu_type
        self.class_name = class_name
        self.init_status = init_status
        self.is_composite = is_composite

    @classmethod
    def parse_name_id_path(cls, name_id_path: str, control_type: Optional[ControlType] = None):
        name, automation_id, action, init_status = None, None, None, None
        if name_id_path:
            name_id, action_name, _ = StringUtils.split_by_keyword(name_id_path, '{}')
            name = name_id if name_id and not name_id.isdigit() else None
            automation_id = name_id if name_id and name_id.isdigit() else None

            if control_type in {ControlType.TREE, ControlType.TABLE}:
                init_status = InitStatus.of_code(action_name)
            else:
                action = ActionType.of_code(action_name) if action_name else ActionType.default_action(control_type)

        return name, automation_id, action, init_status

    @classmethod
    def parse_id_path(cls, id_path: str, control_type: Optional[ControlType] = None):
        automation_id, action, init_status = None, None, None

        if id_path:
            automation_id, action_name, _ = StringUtils.split_by_keyword(id_path, '{}')
            if control_type in {ControlType.TREE, ControlType.TABLE}:
                init_status = InitStatus.of_code(action_name)
            else:
                action = ActionType.of_code(action_name) if action_name else ActionType.default_action(control_type)

        return automation_id, action, init_status

    def __str__(self) -> str:
        attributes = {k: v for k, v in self.__dict__.items() if v is not None}
        return f"Control({', '.join(f'{k}={v}' for k, v in attributes.items())})"