import datetime
import os
from typing import Optional

from mag_tools.utils.data.string_utils import StringUtils


class ReportInfo:
    name: str
    corporation_name: str

    def __init__(self, root_dir: str, app_name: str, report_name: Optional[str]=None, corporation_name: Optional[str]=None):
        self.root_dir = root_dir
        self.app_name = app_name
        self.name = report_name
        self.corporation_name = corporation_name

        current_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        self.__reports_root = os.path.join(root_dir, 'data', app_name, 'reports', f'{current_time}')

        os.makedirs(self.__reports_root, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.result_dir, exist_ok=True)

    @property
    def report_dir(self)->str:
       return os.path.join(self.__reports_root, 'report')

    @property
    def result_dir(self)->str:
        return os.path.join(self.__reports_root, 'result')

    @property
    def html_file(self)->str:
        return os.path.join(self.__reports_root, 'report.html')

    @property
    def url(self)->str:
        relative_dir = StringUtils.pick_tail(self.report_dir, '\\data\\').replace('\\', '/')
        return f'http://localhost/{relative_dir}/index.html'
