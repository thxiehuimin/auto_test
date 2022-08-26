import os
import requests
import logging
import time
# 根据键查找值
from common.config_path import file_data_dir



# 发送请求
def http_request(method, url, params, raw, file, headers):
    resp = None
    if method.upper() == 'GET':
        try:
            resp = requests.get(url, headers=headers, params=params)
        except Exception as e:
            logging.error('get请求出错了：{}'.format(e))
    elif method.upper() == 'POST':
        try:
            if file is not None:
                del headers["Content-Type"]
                file = {'file': open(os.path.join(file_data_dir, file), "rb")}
                resp = requests.post(url=url, params=raw, files=file, headers=headers)
                # resp = requests.post(url=url, params=raw, files=file, headers=headers)
            else:
                resp = requests.post(url=url, json=raw, headers=headers)
                # resp = requests.post(url=url, data=raw.encode(), headers=headers)
        except Exception as e:
            logging.error('post请求出错了：{}'.format(e))
    else:
        logging.info('不支持该种方式')
        resp = None
    time.sleep(0.1)
    return resp


