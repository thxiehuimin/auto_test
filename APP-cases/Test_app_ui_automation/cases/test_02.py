# coding=utf-8

import logging
import os
import pytest
import allure
import config_path
from common.analysis_excel import AnalysisExcels


@allure.epic("场景2")  # 测试报告：特性场景名称
@allure.feature("其他模块")  # 测试报告：模块名
# @pytest.mark.flaky(reruns=3, reruns_delay=5)
class Test01:
    filename = os.path.join(config_path.test_data_dir, "test_case_app.xlsx")  # 获取测试数据路径
    analysis_excels = AnalysisExcels(filename)  # 创建AnalysisExcels对象，用于操作excel
    analysis_excels.clear_excel_value()  # 清除用例表的执行信息
    case_data = analysis_excels.get_case_data()  # 获取测试数据

    @allure.story("其他操作")  # 标记
    @pytest.mark.parametrize('datas', case_data)
    def test01(self, datas, func):
        self.lib = func
        step_data = datas["step_data"]  # 获取步骤
        case_name = datas["case_name"]  # 获取用例名
        allure.dynamic.title(case_name)  # 在测试报告中自定义测试模块名称
        try:
            for index, step_data in enumerate(step_data):  # 遍历步骤数据，循环执行步骤
                try:
                    with allure.step(f"步骤{index + 1}:{step_data[0]}"):  # 在测试报告中自定义测试步骤名称
                        logging.info(f"开始执行步骤：{step_data[0]}")  # 打印日志
                    self.lib.run(*step_data[1:])  # 运行测试数据中的名为关键字的方法
                    self.analysis_excels.write_step_time(case_name, index + 2)  # 在测试数据中写入执行时间
                    self.analysis_excels.write_step_result(sheet_name=case_name, row=index + 2,
                                                           col=config_path.case_step_result,
                                                           result="PASS")  # 在测试数据中写入执行结果
                except Exception as error:
                    screen_path = os.path.join(config_path.screen_dir, "error_screenshot.png")  # 定义截图存放的路径
                    self.lib.run("save_screenshot", screen_path)  # 保存截图
                    self.analysis_excels.write_step_time(case_name, index + 2)  # 在测试数据中写入执行时间
                    self.analysis_excels.write_step_result(sheet_name=case_name, row=index + 2,
                                                           col=config_path.case_step_result,
                                                           result="FALSE")  # 在测试数据中写入执行结果

                    with open(file=screen_path, mode="rb") as f:  # 将错误截图放到测试报告中
                        allure.attach(body=f.read(), name="错误截图", attachment_type=allure.attachment_type.PNG)
                    self.lib.run("refresh")  # 刷新页面
                    raise Exception(f"有错误{step_data},{error}")  # 抛出异常
        except Exception:
            raise
        finally:
            self.analysis_excels.write_case_result(case_name)  # 将执行结果写入汇总表中
            logging.info("将执行结果写入汇总表中")
