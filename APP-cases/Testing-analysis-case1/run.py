# coding=utf-8
import sys
import pytest
import os
import time
from config_path import report_json_dir, report_html_dir, test_case_dir
from allure_pytest import plugin as allure_plugin
import pytest_repeat as repeat

if __name__ == '__main__':
    if hasattr(sys, 'frozen'):
        pytest.main(args=['-vs', "-x", test_case_dir, '--alluredir={}'.format(report_json_dir), '--clean-alluredir'],
                    plugins=[allure_plugin, repeat])
    else:
        pytest.main(args=['-vs', "-x", test_case_dir, '--alluredir={}'.format(report_json_dir), '--clean-alluredir'])
    time.sleep(1)
    os.system("allure generate {} -o {} --clean".format(report_json_dir, report_html_dir))

