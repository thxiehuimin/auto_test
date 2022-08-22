# coding=utf-8

import os
import sys


def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)  # 使用pyinstaller打包后的exe目录
    return os.path.dirname(os.path.abspath(__file__))  # 没打包前的py目录


# 根路径
# root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_path = app_path()
# 数据路径
test_data_dir = os.path.join(root_path, "data")
# 上传文件路径
file_data_dir = os.path.join(root_path, "data", "file_data")
# 日志路径
logs_dir = os.path.join(root_path, 'output')
# 失败截图
screen_dir = os.path.join(root_path, "output")
# 用例汇总工作表名称
cases_sheet_name = '用例汇总统计'
# excel表中关键字所在的列
keyword_col = 2
# excel表中操作值所在的列
action_col = 6
# excel表中操作时间所在的列
action_time_col = 7
# excel表中执行结果所在的列
case_step_result = 8
# 汇总表中是否执行所在的列数
case_is_col = 5
# 汇总表中操作步骤的所在列数
case_step_name_col = 4
# 汇总表中的执行结果所在列数
case_result_col = 7

# 测试报告路径
report_html_dir = os.path.join(root_path, "reports")
report_json_dir = os.path.join(root_path, "temp")
test_case_dir = os.path.join(root_path, "cases")
