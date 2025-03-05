import unittest
from mag_test.model.control_type import ControlType
from mag_test.model.action_type import ActionType
from mag_test.bean.element_info import ElementInfo  # 假设你的类文件名为element_info.py

class TestElementInfo(unittest.TestCase):

    def test_button(self):
        element_info = ElementInfo(
            element_type=ControlType.BUTTON,
            name_path="新建工区"
        )

        self.assertEqual(element_info.main_type, ControlType.BUTTON)
        self.assertEqual(element_info.main_name, "新建工区")
        self.assertEqual(element_info.main_action, ActionType.CLICK)
        self.assertEqual(element_info.child_info, None)
        self.assertEqual(element_info.pop_menu, None)
        self.assertEqual(element_info.value, None)
        self.assertEqual(element_info.pop_window, None)

    def test_dir(self):
        element_info = ElementInfo(
            element_type=ControlType.FILE,
            name_path="{DELETE_DIR}"
        )

        self.assertEqual(element_info.main_type, ControlType.FILE)
        self.assertEqual(element_info.main_name, None)
        self.assertEqual(element_info.main_action, ActionType.DELETE_DIR)
        self.assertEqual(element_info.child_info, None)
        self.assertEqual(element_info.pop_menu, None)
        self.assertEqual(element_info.value, None)
        self.assertEqual(element_info.pop_window, None)

    def test_tree_name(self):
        element_info = ElementInfo(
            element_type=ControlType.BUTTON,
            name_path="树视图{SELECT}/树项{CLICK}/新建方案组",
            parent_name='XPane', parent_type=ControlType.PANE,
        )

        self.assertEqual(element_info.main_type, ControlType.BUTTON)
        self.assertEqual(element_info.main_name, "树视图")
        self.assertEqual(element_info.main_action, ActionType.SELECT)
        self.assertEqual(element_info.child_name, '树项')
        self.assertEqual(element_info.child_action, ActionType.CLICK)
        self.assertEqual(element_info.pop_menu.name, '新建方案组')
        self.assertEqual(element_info.pop_menu.action, ActionType.CLICK)
        self.assertEqual(element_info.parent_name, 'XPane')
        self.assertEqual(element_info.parent_type, ControlType.PANE)
        self.assertEqual(element_info.value, None)
        self.assertEqual(element_info.pop_window, None)

if __name__ == '__main__':
    unittest.main()
