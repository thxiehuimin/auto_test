import re
import json
from urllib import parse
from flask import Flask ,request as request_
from common.config_path import host, login_ip
import sqlite3
import time
import os
import threading
from config_path import test_data_path
import _thread

app = Flask(__name__)
app.debug = True
data = []

@app.route("/", methods=["GET", "POST"])
def hello_world():
    url = request_.form.get("url")
    headers = request_.form.get("headers")
    RequestBody = request_.form.get("RequestBody")     # 客户端的请求参数
    ResponseBody = request_.form.get("ResponseBody")   # 服务器的返回结果

    global data
    if (host in url or login_ip in url) and ".js" not in url and ".ico" not in url and ".png" not in url and ".css" not in url and ":80" not in url and "websocket" not in url:
        if "queryDepositContents" not in url and "analysis-app" not in url:
            data.append(get_data(url, headers, RequestBody, ResponseBody))
            # ["module", "checkout", "host", "interface_name", "interface_address", "method", "parameters", "files", "headers", "RequestBody", "ResponseBody"]
            请求 = {"host": data[-1][2], "interface_name": data[-1][3], "interface_address": data[-1][4], "method": data[-1][5], "params": data[-1][6], "files": data[-1][7],"headers": data[-1][8], "RequestBody": data[-1][9]}
            响应 = data[-1][-1]
            print("[")
            print("**interface_name:  ", data[-1][4])
            # print("请求-->", 请求)
            # print("响应<--", 响应)
            print("]")

    return "Hello"


def get_data(url, headers, RequestBody, ResponseBody):
    json_dumps = lambda value: json.dumps(value, ensure_ascii=False, indent=4)
    # 解析js unicode-escape 转码
    parse_unquote = lambda value: parse.unquote(value.replace('%u', '\\u').encode().decode('unicode-escape'))

    def url_analysis(url):
        url_list = url.split('/')
        host = url_list[0]  # Ip
        interface_name = url_list[-1]  # 接口名
        interface_address = '/'+'/'.join(url_list[1:])  # 接口地址
        parameters = None
        if "?" in url:
            interface_name = interface_name.split('?')[0]
            interface_address = interface_address.split('?')[0]
            parameters = url.split("?", 1)[1]
            parameters = json_dumps(dict(parse.parse_qsl(parameters)))
        return host, interface_name, interface_address, parameters

    def headers_analysis(headers):
        method = headers.split(" ")[0].upper()  # 提交方式 get / post
        headers_dict = {}
        headers_list = headers.split("\n")
        for line in headers_list[1:-1]:
            key = line.split(": ")[0]
            headers_dict[key] = line.replace(key + ": ", "").replace("\r", "")
        return method, json_dumps(headers_dict)

    def request_analysis(RequestBody):
        Request = None
        file_list = []
        # file 解析
        if "name=\"file\"" in RequestBody:
            p = re.compile("filename=\"(.*)\"")
            files = p.findall(RequestBody)
            for file in files:
                file_list.append(parse_unquote(file))
        file_re = file_list[0] if file_list else None
        try:
            null = None
            true = True
            false = False
            Request = parse_unquote(RequestBody)
            Request = json_dumps(eval(Request)) if Request else None
        except:
            print("转换Request失败: ", "\n")
            Request = str(Request).replace("\n", "").replace('\\"', '"')[:]
        return file_re, Request

    def response_analysis(ResponseBody):
        # Extract 解析
        Extract = None
        if "token" in ResponseBody:
            Extract = {"token": '["data"][0]["token"]'}
        elif "fileId" in ResponseBody:
            Extract = {"fileId": '["data"][0]["fileId"]'}
        elif "getUserInfoForNew" in url:
            Extract = {"entId": '["data"][0]["entId"]'}
        Extract = json_dumps(Extract) if Extract else None
        try:
            Response = parse_unquote(ResponseBody)
        except:
            pass
        try:  # 如果返回值是json 解析请求
            null = None
            true = True
            false = False
            Response = json_dumps(eval(Response)) if Response else None
        except:
            print("转换Response失败: ", "\n")
            Response = str(Response).replace("\n", "").replace('\\"', '"')[:]


        return Response, Extract

    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    host, interface_name, interface_address, parameters = url_analysis(url)
    method, headers_dict = headers_analysis(headers)
    files, Request_dict = request_analysis(RequestBody)
    Response_dict, Extract_dict = response_analysis(ResponseBody)

    interface_data = [create_time, None, None, host, interface_name, interface_address, method, parameters, files, headers_dict, Request_dict, Response_dict, Extract_dict]
    return interface_data


class DBHhelper():
    # conn = ""
    # csr = ""

    def __init__(self, table_name):
        print(test_data_path)
        dbName = test_data_path.split('\\')[-1]
        self.conn = sqlite3.connect(test_data_path, check_same_thread=False)
        self.csr = self.conn.cursor()
        self.table_name = table_name
        print("Database ", dbName, " created successfully!")

    def create_table(self):
        query_sql = F"CREATE TABLE IF NOT EXISTS {self.table_name} (create_time date, module text,checkout text,host text,\
                 interface_name text, interface_address text, method text, parameters text, files text ,headers text, RequestBody text,\
                 ResponseBody text, Extract text)"
        self.csr.execute(query_sql)
        self.conn.commit()
        print("table ", self.table_name, " created successfully!")

    def add_record(self, data):
        query_sql = F"INSERT INTO {self.table_name} VALUES ('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}',\
        '{data[4]}', '{data[5]}', '{data[6]}', '{data[7]}', '{data[8]}', '{data[9]}', '{data[10]}', '{data[11]}', '{data[12]}');"
        self.csr.execute(query_sql)
        self.conn.commit()

    def get_record(self):
        query_sql = F"select * from {self.table_name}"
        self.csr.execute(query_sql)
        self.conn.commit()
        for row in self.csr:
           print(row)

    # def updateRecord(self):
    # def deleteRecord(self):

    def Dbclose(self):
        self.conn.close()


def write_db(threadname, delay):
    global data
    while True:
        time.sleep(delay)
        lock = threading.Lock()
        lock.acquire(True)
        for d in data:
            test_db.add_record(d)
            print(threadname, "record inserted successfully: ", d[4])
        lock.release()
        data = list()


if __name__ == '__main__':
    # table_name = "login"
    table_name = "qrt_fix_asset"
    test_db = DBHhelper(table_name)
    test_db.create_table()
    _thread.start_new_thread(write_db, ("写入db-", 10,))
    # test_db.Dbclose()
    app.run(host="localhost", port="5500")
