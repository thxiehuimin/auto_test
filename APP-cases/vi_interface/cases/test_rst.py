import json
import logging
import time
import allure
import pytest
import ast
from common.base import find_key, http_request
from common.dbutil import implement_sql
from common.open_excel import read_data
from common.config_path import test_data_path, http_url

test_data = read_data(test_data_path)  # 获取测试数据


class TestRst:
    # 存储传参
    extract = dict()

    # 处理param
    def get_params(self, params):
        for key, value in self.extract.items():
            params = params.replace('{{' + key + '}}', value)
        return params

    # 处理header
    def get_header(self, headers):
        for key, value in self.extract.items():
            headers = headers.replace('{{' + key + '}}', value)
        # 将读取出来的headers转换成字典
        headers = ast.literal_eval(headers)
        return headers

    @pytest.mark.parametrize('case', test_data)
    def test_cases(self, case):
        # 在测试报告中自定义测试模块名称
        allure.dynamic.title(case.get('ApiName'))
        # 如果接口名称为等待，则执行等待
        if case.get('ApiName') == '等待':
            s = int(case.get('Raw'))
            logging.info('---等待{}秒'.format(s))
            time.sleep(s)
        else:
            # 获取url地址
            url = http_url + case.get('path')
            method = case['Method']
            params, form_data, files = case['Params'], case['FormData'], case['Files']
            # 如果参数不为空，则赋值
            if case['Raw'] is not None:
                raw = self.get_params(case['Raw'])
            else:
                raw = ''

            # 处理Headers值
            headers = self.get_header(case['Headers'])
            # 发起请求
            logging.info('-------------------------------------------------------------------------------------------')
            logging.info('---接口名称:{}'.format(case.get('ApiName')))
            logging.info('---接口URL:{}'.format(url))
            logging.info('---接口入参:{}'.format(params))
            logging.info('---请求方式:{}'.format(method))
            logging.info('---请求头headers:{}'.format(headers))
            logging.info('---预期结果:{}'.format(case["ExpectedResult"]))
            res = http_request(method, url, params, raw, form_data, files, headers)
            logging.info("---响应数据：" + res.text)

            # 如果sql不为空，则执行sql
            if case['Sql'] is not None:
                sql_list = json.loads(case['sql'])
                for key, value in sql_list.items():
                    implement_sql(key, value)

            # 断言
            for key, value in json.loads(case.get('ExpectedResult')).items():
                try:
                    if isinstance(value, str):
                        assert value in find_key(res.json(), key)
                    else:
                        assert float(value) == find_key(res.json(), key)
                except Exception as e:
                    logging.error('断言失败！异常原因:{}'.format(e))
                    raise

            # 提取参数
            if case['Extract'] is not None:
                list_data = json.loads(case['Extract'])
                for key, value in list_data.items():
                    st = find_key(res.json(), value)
                    if st is not None:
                        self.extract[key] = st
                        logging.info('---添加了变量：' + key + '：' + st)
