import os.path
from typing import Optional

from mag_tools.utils.file.file_utils import FileUtils
from mag_tools.utils.file.json_file_utils import JsonFileUtils

from mag_test.bean.report_info import ReportInfo


class ReportStyle:
    @staticmethod
    def update(report_info: ReportInfo):
        ReportStyle.__update_window_title(report_info.root_dir, report_info.report_dir, report_info.corporation_name)
        ReportStyle.__update_overview_title(report_info.report_dir, report_info.name)

    # 修改报告的窗口标题
    @staticmethod
    def __update_window_title(root_dir: str, report_dir:str, corporation_name:Optional[str]):
        # 读取html文件
        with open(os.path.join(report_dir, 'index.html'), 'r+', encoding='utf-8') as f:
            # 先保存html的内容
            lines = f.readlines()
            # 定义下标变量，方便后边的数据更替
            i = -1
            for line in lines:
                i += 1
                # 寻找html页面的title标签
                if '<title>' in line:
                    # 定义原始标题变量
                    old_title = ''
                    # html里的title标签之前有4个空格，所以从下标为11处截取
                    for s in line[11:]:
                        # 若字符为<则退出循环
                        if s == '<':
                            break
                        # 原始标题-拨云见日
                        old_title += s

                    # 正式替换标题
                    if corporation_name:
                        lines[i] = line.replace(old_title, corporation_name)

                    # 修改标题后的html内容
                    new_lines = lines
            # 指针放在文件开始的地方
            f.seek(0)
            # 清空原来的html文件内容
            f.truncate()
            # 将修改标题后的内容重新写入html文件
            for new_line in new_lines:
                f.write(new_line)

        # 替换favicon.ico文件
        FileUtils.copy_and_overwrite(os.path.join(root_dir, 'data', 'favicon.ico'), os.path.join(report_dir, 'favicon.ico'))

    # 修改报告的Overview标题
    @staticmethod
    def __update_overview_title(report_dir, report_name):
        JsonFileUtils.update_params(os.path.join(report_dir, 'widgets', 'summary.json'), {'reportName': report_name})