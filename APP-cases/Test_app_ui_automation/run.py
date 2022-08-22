# coding=utf-8
import pytest
import os
from config_path import report_json_dir, report_html_dir, test_case_dir

if __name__ == '__main__':
    pytest.main(args=['-vs', "-x", test_case_dir, '--alluredir={}'.format(report_json_dir), '--clean-alluredir'])
    os.system("allure generate {} -o {} --clean".format(report_json_dir, report_html_dir))


