import sqlite3
import pandas as pd
from common.config_path import test_data_path, cases_table_name


def read_data(test_data_path):  # section 配置文件里面的片段名 可以根据你的指定来执行具体的用例
    """从Excel读取数据，有返回值"""
    test_data = []
    case_list = []
    conn = sqlite3.connect(test_data_path, check_same_thread=False)
    csr = conn.cursor()
    query_sql = F"select * from {cases_table_name}"
    case_table = pd.read_sql(query_sql, con=conn)
    for row in range(case_table.shape[0]):
        is_execute = case_table.loc[row]["is_execute"]
        if is_execute == "y":
            case_name = case_table.loc[row]["test_table"]
            case_list.append(case_name)

    for case_name in case_list:
        query_sql = F"select * from {case_name}"
        case_data = pd.read_sql(query_sql, con=conn)

        for row in range(case_data.shape[0]):  # case_data.shape[0]
            row_data = {}
            row_data['Modular'] = case_data.loc[row]["module"]
            row_data['ApiName'] = case_data.loc[row]["interface_name"]
            row_data['path'] = case_data.loc[row]["interface_address"]
            row_data['Method'] = case_data.loc[row]["method"]
            row_data['Headers'] = case_data.loc[row]["headers"]
            row_data['Params'] = case_data.loc[row]["parameters"]
            row_data['Raw'] = case_data.loc[row]["RequestBody"]
            row_data['Files'] = case_data.loc[row]["files"]
            row_data['ExpectedResult'] = case_data.loc[row]["ResponseBody"]
            # {"fileId":'["data"][0]["fileId"]'}
            row_data['Extract'] = case_data.loc[row]["Extract"]
            test_data.append(row_data)

    conn.close()
    return test_data


if __name__ == '__main__':
    test_datas = read_data(test_data_path)  # 获取测试数据
    for k in test_datas:
        print(k)