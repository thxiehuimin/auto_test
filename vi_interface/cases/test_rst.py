import json
import logging
import time
import allure
import pytest
from common.base import http_request
from common.open_db import read_data
from common.config_path import test_data_path, http_url

test_data = read_data(test_data_path)  # 获取测试数据


class TestRst:
    # 存储传参
    extract = dict()

    # db-处理header
    def get_header(self, headers):
        headers = {"Content-Type":"application/json"}
        for key, value in self.extract.items():
            if key == "token":
                headers["Authorization"] = "Bearer " + value
        return headers

    # db- 处理raw
    def get_params(self, raw):
        # print("----------------------",raw)
        raw = json.loads(raw)
        for key, value in self.extract.items():
            if key in raw.keys():
                raw[key] = value
        return raw



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
            method = case['Method'].upper()
            params, files = case['Params'], case['Files']
            params = json.loads(params) if params != "None" else None
            files = files if files != "None" else None
            if files is not None:
                raw = {"entId": self.extract["entId"]}
            else:# 如果参数不为空，则赋值
                raw = self.get_params(case['Raw']) if case['Raw'] != "None" else None

            # 处理Headers值
            headers = self.get_header(case['Headers'])
            # 发起请求
            logging.info('-------------------------------------------------------------------------------------------')
            logging.info('---接口名称：{}'.format(case.get('ApiName')))
            logging.info('---接口URL：{}'.format(url))
            logging.info('---请求方式：{}'.format(method))
            if method == 'GET':
                logging.info('---接口入参：{}'.format(params))
            elif method == 'POST':
                logging.info('---接口入参：{}'.format(raw))
            logging.info('---请求头headers：{}'.format(headers))
            logging.info('---预期结果：{}'.format(str(case["ExpectedResult"]).replace("\n", "")[:1000]))
            res = http_request(method, url, params, raw, files, headers)
            logging.info("---响应数据：" + res.text)


            # 断言
            try:
                for key, value in json.loads(case.get('ExpectedResult')).items():
                    if key in ["code", "msg"]:
                        if isinstance(value, str):
                            assert value in res.json().get(key)
            except:
                try:
                    assert case.get('ExpectedResult')[:50] in res.text[:100]
                except Exception as e:
                    logging.error('断言失败！异常原因:{}'.format(e))
                    raise

            if case['Extract'] != "None":
                Extract_data = case['Extract'].replace("\n", "").replace('"[', "'[").replace(']"', "]'")
                list_data = eval(Extract_data)
                for key, value in list_data.items():
                    data = res.json()
                    st = 'data' + value
                    st = eval(st)
                    if st is not None:
                        self.extract[key] = st
                        logging.info('---添加了变量：' + key + '：' + st)