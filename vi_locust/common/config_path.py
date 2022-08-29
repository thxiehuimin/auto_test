import os

# 文件的路径 放到这里
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 测试用例表格的路径
test_data_path = os.path.join(root_path, 'data', 'test_api.db')

# 测试报告的路径
report_path = os.path.join(root_path, 'test_result', 'test_report')

# 上传文件路径
file_data_dir = os.path.join(root_path, "data", "file")

# 日志的路径
log_path = os.path.join(root_path, 'output')


cases_table_name = "test_info"

# flask_fiddler
host = '10.99.31.24:32244'
login_ip = '10.99.31.24:32505'

mysql_pwd = ('127.0.0.1', 3306, 'root', '123456')
