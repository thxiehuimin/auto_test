#coding:utf-8

from locust import HttpUser, TaskSet, task, between
import os
import json
import logging
import requests
import time
from common.open_db import read_data
from common.config_path import test_data_path, host, login_ip, file_data_dir

login_data, test_data = read_data(test_data_path)  # 获取测试数据
def get_user():
    n = 1
    while n:
        user_num = n%len(login_data)
        yield user_num
        n += 1

userNum = get_user()

class WebsiteTasks(TaskSet):
    def on_start(self):
        # 存储传参
        self.extract = dict()
        case_data = login_data[next(userNum)]
        self.test_cases(case_data)

    # db-处理header
    def get_header(self, headers):
        headers = {"Content-Type": "application/json"}
        for key, value in self.extract.items():
            if key == "token":
                headers["Authorization"] = "Bearer " + value
        return headers

    # db- 处理raw
    def get_params(self, raw):
        raw = json.loads(raw)
        for key, value in self.extract.items():
            if key in raw.keys():
                raw[key] = value
        return raw

    def http_request(self, method, url, params, raw, file, headers):
        resp = None
        if method.upper() == 'GET':
            try:
                resp = self.client.get(url=url, headers=headers, params=params)
            except Exception as e:
                logging.error('get请求出错了：{}'.format(e))
        elif method.upper() == 'POST':
            try:
                if file is not None:
                    del headers["Content-Type"]
                    file = {'file': open(os.path.join(file_data_dir, file), "rb")}
                    resp = self.client.post(url=url, headers=headers, params=raw, files=file)
                elif "userLogin" in url:
                    url_new = "http://"+ login_ip + url
                    print(url_new)
                    resp = requests.post(url=url_new, headers=headers, json=raw)
                else:
                    resp = self.client.post(url=url, headers=headers, json=raw)
            except Exception as e:
                logging.error('post请求出错了：{}'.format(e))
        else:
            logging.info('不支持该种方式')
            resp = None
        time.sleep(0.2)
        return resp

    def test_cases(self, case):
        # 如果接口名称为等待，则执行等待
        if case.get('ApiName') == '等待':
            s = int(case.get('Raw'))
            logging.info('---等待{}秒'.format(s))
            time.sleep(s)
        else:
            # 获取url地址
            url = case.get('path')
            method = case['Method'].upper()
            params, files = case['Params'], case['Files']
            params = json.loads(params) if params != "None" else None
            files = files if files != "None" else None
            if files is not None:
                raw = {"entId": self.extract["entId"]}
            else:  # 如果参数不为空，则赋值
                raw = self.get_params(case['Raw']) if case['Raw'] != "None" else None

            # 处理Headers值
            headers = self.get_header(case['Headers'])
            # 发起请求
            logging.info('-------------------------------------------------------------------------------------------')
            logging.info('---接口名称：{}'.format(case.get('ApiName')))
            logging.info('---接口地址：{}'.format(url))
            logging.info('---请求方式：{}'.format(method))
            if method == 'GET':
                logging.info('---接口入参：{}'.format(params))
            elif method == 'POST':
                logging.info('---接口入参：{}'.format(raw))
            logging.info('---请求信息：{}'.format(headers))
            logging.info('---预期结果：{}'.format(str(case["ExpectedResult"]).replace("\n", "").replace("    ", "")[:1000]))
            res = self.http_request(method, url, params, raw, files, headers)
            logging.info("---响应数据：" + res.text[:1000])

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


    @task
    def index1(self):
        for case_data in test_data:
            self.test_cases(case_data)



class WebsiteUser(HttpUser):
    tasks = [WebsiteTasks]
    host = "http://"+host
    wait_time=between(3,3)

if __name__ == '__main__':
    os.system("locust -f cases/test_locust.py --web-host=127.0.0.1")