import os

# 文件的路径 放到这里
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 测试用例表格的路径
test_data_path = os.path.join(root_path, 'data', 'test_api.db')

# 测试报告的路径
report_path = os.path.join(root_path, 'test_result', 'test_report')

# 上传文件路径
file_data_dir = os.path.join(root_path, "data", "file_data")

# 日志的路径
log_path = os.path.join(root_path, 'output')

http_url = 'http://uat.hmtech.com'

# 用例汇总表的名称
cases_sheet_name = '用例汇总表'

# 汇总表中操作步骤的所在列数
case_step_name_col = 2
# 汇总表中是否执行所在的列数
case_is_col = 3


# vi
host = 'uat.hmtech.com'

mysql_pwd = ('127.0.0.1', 3306, 'root', '123456')
