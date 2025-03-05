import json
from typing import Optional

from selenium.webdriver.remote.webelement import WebElement


class ElementUtils:
    @staticmethod
    def get_tree_item_offset(value: str, element: Optional[WebElement] = None) -> Optional[tuple[int, int]]:
        """
        获取子控件的位置偏移
        :param value: 偏移量，格式为：{'offset_x': x, 'offset_y': y}
        :param element: 主控件
        """
        if not value:
            return None

        default_x = element.size['width'] // 2 if element else 0
        default_y = element.size['height'] // 2 if element else 0

        value_map = json.loads(value)
        offset_x = value_map.get('offset_x', default_x)
        offset_y = value_map.get('offset_y', default_y)
        return offset_x, offset_y


    @staticmethod
    def get_main_offset(value: str, element: Optional[WebElement] = None) -> Optional[tuple[int, int]]:
        """
        获取主控件的位置偏移
        :param value: 偏移量，格式为：{'offset_X': x, 'offset_Y': y}
        :param element: 主控件
        """
        if not value:
            return None

        default_x = element.size['width'] // 2 if element else 0
        default_y = element.size['height'] // 2 if element else 0

        value_map = json.loads(value)
        offset_x = value_map.get('offset_X', default_x)
        offset_y = value_map.get('offset_Y', default_y)
        return offset_x, offset_y