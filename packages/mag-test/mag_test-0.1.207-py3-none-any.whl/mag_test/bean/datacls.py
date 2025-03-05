from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RegexObj3:
    there: Optional[str] = field(default=None, metadata={
        "description": "手机",
        "regex": r"^\\d+$",
        "msg": "编号3只能为数字"
    })


@dataclass
class RegexObj2:
    two: Optional[str] = field(default=None, metadata={
        "description": "手机",
        "regex": r"^\\d+$",
        "msg": "编号2只能为数字"
    })
    regex_obj3: Optional[RegexObj3] = field(default=None, metadata={
        "cls": RegexObj3,
    })


@dataclass
class RegexObj1:
    one: Optional[str] = field(default=None, metadata={
        "description": "手机",
        "regex": r"^\\d+$",
        "msg": "编号1只能为数字"
    })


@dataclass
class RegexParams:
    phone: Optional[str] = field(default=None, metadata={
        "description": "手机",
        "regex": r"^1[1-9]\\d{9}$",
        "msg": "手机号不正确"
    })
    name: str = field(default=None, metadata={
        "description": "姓名",
        "option": ["张三", "李四", "王五"],
        "msg": "姓名只能为张三，李四，王五"
    })
    regex_obj1: Optional[RegexObj1] = field(default=None, metadata={
        "cls": RegexObj1,
    })
    regex_obj2: Optional[RegexObj2] = field(default=None, metadata={
        "cls": RegexObj2,
    })


@dataclass
class PrimaryParams:
    uuid: Optional[int] = field(default=None, metadata={
        "description": "模拟标识",
        "min": 6,
        "max": 64,
        "msg": "大小必须在6到64之间",
        "exits_ok": True
    })
    password: Optional[str] = field(default=None, metadata={
        "description": "模拟标识",
        "min_len": 6,
        "max_len": 18,
        "exits_ok": True,
        "msg": "密码长度必须大于6小于10"
    })
    regex_params: Optional[RegexParams] = field(default=None, metadata={
        "cls": RegexParams,
    })
    regex_params2: Optional[RegexParams] = field(default=None, metadata={
        "cls": RegexParams,
    })
