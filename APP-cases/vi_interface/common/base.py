import ast
import json
import os

import requests
import logging

# 根据键查找值
from common.config_path import file_data_dir


def find_key(data, key):
    for i in key.split('.'):
        if i.isdigit():
            i = int(i)
            data = data[i]
        else:
            data = data.get(i)
        if type(data) == str or type(data) == int or type(data) == float:
            return data


# 发送请求
def http_request(method, url, params, raw, form_data, file, headers):
    resp = None
    if method.upper() == 'GET':
        try:
            if params is not None:
                url = url + '?' + params
            resp = requests.get(url, headers=headers)
        except Exception as e:
            logging.error('get请求出错了：{}'.format(e))
    elif method.upper() == 'POST':
        try:
            if params is not None:
                url = url + '?' + params
            if file is not None:
                file = {'file': open(os.path.join(file_data_dir, file), "rb")}
                resp = requests.post(url=url, params=ast.literal_eval(raw), files=file, headers=headers)
            else:
                resp = requests.post(url=url, data=raw.encode(), headers=headers)
        except Exception as e:
            logging.error('post请求出错了：{}'.format(e))
    else:
        logging.info('不支持该种方式')
        resp = None
    return resp


