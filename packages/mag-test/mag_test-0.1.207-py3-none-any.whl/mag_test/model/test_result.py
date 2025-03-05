from mag_tools.model.base_enum import BaseEnum


class TestResult(BaseEnum):
    SUCCESS = ('Success', '成功')
    FAIL = ('Fail', '失败')
    SKIP = ('Skip', '跳过')
    UNKNOWN = ('Unknown', '未知')
