# coding=utf-8
import traceback
import logging
import time
import win32con
import win32gui
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import config_path
import os
from email.parser import Parser
import poplib
import base64
import re

class BasePageMethod(object):


    def run(self, keyword, *args):  # 基于反射调用关键字函数
        getattr(self, keyword)(*args)

    def open_browser(self, browser_name):  # 打开浏览器
        try:
            if browser_name[0] == '$':
                browser_name = browser_name[1:]
                options = Options()
                options.add_argument('--headless')  # 设置无头模式
                options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
                options.add_argument("--disable-blink-features=AutomationControlled")  # 浏览器环境补齐
                self.driver = getattr(webdriver, browser_name)(options=options)
                logging.info(f"使用无头模式打开{browser_name}浏览器")
                self.driver.set_window_size(1920, 1500)
                logging.info('将浏览器窗口设置为1920*1500')
            else:
                self.driver = getattr(webdriver, browser_name)()
                logging.info(f"打开{browser_name}浏览器")
                self.driver.maximize_window()
                logging.info('设置窗口最大化')

        except Exception as e:
            logging.error(f"无法打开{browser_name}浏览器,异常原因：{e}")
            raise

    def implicitly_wait(self, second):
        try:
            self.driver.implicitly_wait(second)
            logging.info(f"设置隐式等待{second}秒")
        except Exception as e:
            logging.error(f"设置隐式等待失败,异常原因：{e}")
            raise

    @staticmethod
    def wait(s):  # 等待
        time.sleep(int(s))
        logging.info(f"等待{s}秒")

    def open_url(self, url):  # 打开url
        try:
            self.driver.get(url)
            logging.info(f"打开URL：{url}")

        except Exception as e:
            logging.error(f"无法打开URL：{url},异常原因：{e}")
            raise

    def refresh(self):
        self.driver.refresh()
        logging.info("刷新页面")

    def locator(self, type_, express):  # 定位元素
        try:
            if type_ == "css selector":
                el = self.vi_locator(type_, express)
                logging.info('定位元素{}成功!'.format((type_, express)))
                return el
            else:
                time.sleep(0.5)
                element = self.driver.find_element(type_, express)
                logging.info('定位元素{}，成功!'.format((type_, express)))
                return element

        except Exception as e:
            logging.error(f"定位元素{type_, express}失败，原因:{e}")
            raise


    def action_input(self, type_, express, value):
        el = self.locator(type_, express)
        ActionChains(self.driver).click(el).pause(1).send_keys(value).perform()

    def input(self, type_, express, value):  # 输入
        try:
            self.locator(type_, express).send_keys(value)
            logging.info(f"在元素{type_, express}中输入:{value}")
        except Exception as e:
            logging.error(f"在元素{type_, express}中输入{value}失败,原因：{e}")
            raise

    def delete_input(self, type_, express, value):  # 清空后输入
        try:
            el = self.locator(type_, express)
            el.send_keys(u'\ue009', 'a')
            el.send_keys(u'\ue017')
            logging.info(f"清除元素{type_, express}中的内容")
            el.send_keys(str(value))
            logging.info(f"在元素{type_, express}中输入:{value}")
        except Exception as e:
            logging.info(f"清除元素{type_, express}中的内容失败，原因:{e}")
            raise

    def clear_input(self, type_, express, value):  # 清空后输入
        try:
            self.locator(type_, express).clear()
            logging.info(f"清除元素{type_, express}中的内容")
            self.input(type_, express, value)
        except Exception as e:
            logging.info(f"清除元素{type_, express}中的内容失败，原因:{e}")
            raise

    def click(self, type_, express):  # 点击
        try:
            try:
                self.locator(type_, express).click()
                logging.info(f"点击元素{type_, express}成功")
            except Exception as e:
                logging.info(f"点击元素{type_, express}失败，错误原因{e}，2秒后正在重试")
                time.sleep(0.5)
                self.locator(type_, express).click()
                logging.info(f"点击元素{type_, express}成功")
        except Exception as e:
            logging.error(f"点击元素{type_, express}失败,原因：{e}")
            logging.info("不需要点击")
            # raise

    def click_(self, type_, express):  # 点击
        try:
            self.locator(type_, express).click()
            logging.info(f"点击元素{type_, express}成功")
        except Exception as e:
            logging.error(f"点击元素{type_, express}失败,原因：{e}")
            raise

    def click_refresh(self, type_, express):
        for i in range(5):
            try:
                self.click_(type_, express)
                time.sleep(3)
                break
            except:
                logging.info(f'页面空白，即将刷新，已刷新{i+1}次')
                self.refresh()
                time.sleep(5)

    def js_click(self, type_, express):  # 使用js点击
        try:
            try:
                self.driver.execute_script("arguments[0].click()", self.locator(type_, express))
                logging.info(f"点击元素{type_, express}")
            except Exception as e:
                logging.info(f"js点击元素{type_, express}失败，错误原因{e}，2秒后正在重试")
                time.sleep(2)
                self.driver.execute_script("arguments[0].click()", self.locator(type_, express))
                logging.info(f"点击元素{type_, express}")
        except Exception as e:
            logging.error(f"使用js点击元素{type_, express}失败,原因：{e}")
            raise

    def save_screenshot(self, screen_path):  # 保存截图
        self.driver.save_screenshot(screen_path)
        logging.info(f"保存错误截图成功，截图所在路径：{screen_path}")


    def move_element(self, type_, express):  # 将鼠标悬停在元素上
        try:
            el = self.locator(type_, express)
            ActionChains(self.driver).move_to_element(el).perform()
            logging.info(f"将鼠标悬停在元素{type_, express}")
        except Exception as e:
            logging.error(f"将鼠标悬停在元素{type_, express},原因：{e}")
            raise

    def upload_file(self, type_, express, file_name):
        try:
            file_path = os.path.join(config_path.file_data_dir, file_name)
            self.locator(type_, express).send_keys(file_path)
            logging.info(f"在元素{type_, express}中输入:{file_name}")
        except Exception as e:
            logging.error(f"在元素{type_, express}中输入{file_name}失败,原因：{e}")
            raise

    def locators(self, type_, express):  # 定位多个元素
        try:
            if type_[0] == '$':
                elements = WebDriverWait(self.driver, 10, 0.5).until(
                    lambda el: self.driver.find_elements(type_[1:], express), message='TimeoutException')
                logging.info('使用显示等待定位元素{}，成功!'.format((type_[1:], express)))
                return elements
            else:
                elements = self.driver.find_elements(type_, express)
                # el_list = [e.text for e in elements]
                # print("-------el_list:", el_list)
                logging.info('定位元素{}，成功!'.format((type_, express)))
                return elements

        except Exception as e:
            logging.error(f"定位元素{type_, express}失败，原因:{e}")
            raise

    def wait_ele_visible(self, type_, express, value=15):  # 等待元素可见
        try:
            if type_[0] == '$':
                type_ = type_[1:]
            WebDriverWait(self.driver, value, 0.5).until(lambda el: self.driver.find_element(type_, express),
                                                         message='TimeoutException')
            logging.info(f"寻找元素{type_, express}成功!")
        except Exception as e:
            logging.error(f"寻找元素{type_, express}失败，原因:{e}")
            # raise

    def check_list_text(self, type_, express, value):  # 校验表中元素
        els = self.locators(type_, express)
        page_data = []
        for i in els:
            # print("----i.text:", i.text)
            num_str = i.text.replace(',', '').replace('-', '', 1).replace('%', '').replace('/\n', ',').replace(' ',',').replace('/n', ',')
            # if num_str[:num_str.find('.')].isnumeric() and num_str[num_str.find('.') + 1:].isnumeric():
            if num_str is not None:
                page_data.append(i.text)

        if str(page_data) == value:  # 对比预期结果和实际结果
            logging.info("数据校验正确")
        else:
            logging.error(f"数据校验不正确，页面中的数据:{page_data}不等于预设的数据：{value}")
            # raise

    def check_list_value(self, type_, express, value):  # 校验表中元素
        els = self.locators(type_, express)
        page_data = []
        for i in els:
            num_str = i.text.replace(',', '').replace('-', '', 1).replace('%', '').replace('/\n', ',').replace(' ',
                                                                                                               ',').replace(
                '/n', ',')
            if num_str[:num_str.find('.')].isnumeric() and num_str[num_str.find('.') + 1:].isnumeric():
                if num_str is not None:
                    page_data.append(i.text)

        if str(page_data) == value:  # 对比预期结果和实际结果
            logging.info("数据校验正确")
        else:
            logging.error(f"数据校验不正确，页面中的数据:{page_data}不等于预设的数据：{value}")
            # raise

    @staticmethod
    def get_code():
        # 头部信息已取出
        def get_body(msg):
            value = msg.get_payload()[0].get_payload()[0].get_payload()
            return value

        # 输入邮件地址, 口令和POP3服务器地址:
        from_email = "adam.zhang@huamengtech.net"
        from_email_pwd = "jie@1113"
        pop_server = "mail.huamengtech.net"

        server = poplib.POP3(pop_server)
        server.set_debuglevel(0)
        # 设置实例的调试级别。这控制打印的调试输出量。默认值0不产生调试输出。值1产生适量的调试输出，通常每个请求都有一行。值2或更高会产生最大调试输出量，记录在控制连接上发送和接收的每行。
        # print(server.getwelcome().decode("utf-8"))
        # 欢迎信息
        # 登录
        server.user(from_email)
        server.pass_(from_email_pwd)
        resp, mails, octets = server.list()  # 返回邮件数量和每个邮件的大小

        resp, lines, octets = server.retr(len(mails))  # 返回由参数标识的邮件的全部文本

        msg_content = b"\r\n".join(lines).decode("utf-8", "ignore")  # byte字符串
        msg_ = Parser().parsestr(msg_content)

        body = get_body(msg_)
        code_str = base64.b64decode(body).decode('utf-8')
        code = re.findall(r'\d+', code_str.split()[0])[0]
        server.close()
        return code

    def login_prd(self, parameter):
        account, password, express1, express2, express3, express4, express5, express6, express7 = parameter.split(',')
        for i in range(10):
            self.input('xpath', express1, account)  # 输入用户名
            self.input('xpath', express2, password)  # 输入密码
            self.action_move_slide('xpath', express3)  # 拖动滑块
            self.click('xpath', express4)  # 点击获取验证码
            self.wait(25)
            if i == 0:
                self.driver.execute_script("window.open('http://mail.huamengtech.net/','_blank');")

                # 切换到指定句柄的窗口
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.find_element('xpath', '//input[@id="f_user"]').send_keys('adam.zhang')
                self.driver.find_element('xpath', '//input[@id="f_pass"]').send_keys('jie@1113')
                self.driver.find_element('xpath', '//div[contains(text(),"登录")]').click()
                self.driver.find_element('xpath', '//*[@id="menuitem_msglist_inbox"]').click()
                code = self.driver.find_element('xpath', '//*[contains(text(),"【华盟科技】验证码：")]').text[10:16]
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.input('xpath', express5, code)
            else:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.click('xpath', "//*[text()='刷新']")
                code = self.driver.find_element('xpath', '//*[contains(text(),"【华盟科技】验证码：")]').text[10:16]
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.input('xpath', express5, code)

            self.click('xpath', express6)  # 点击阅读协议
            self.click('xpath', express7)  # 点击登录
            try:
                self.wait_ele_visible('xpath', '//*[contains(text(),"成功")]')
                break
            except:
                logging.error('获取验证码错误，即将开始重试,已重试:{}次'.format(i))
                self.refresh()

    def obtain_code(self):
        self.driver.execute_script("window.open('http://mail.huamengtech.net/','_blank');")

        # 切换到指定句柄的窗口
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.find_element('xpath', '//input[@id="f_user"]').send_keys('adam.zhang')
        self.driver.find_element('xpath', '//input[@id="f_pass"]').send_keys('jie@1113')
        self.driver.find_element('xpath', '//div[contains(text(),"登录")]').click()
        self.driver.find_element('xpath', '//*[@id="menuitem_msglist_inbox"]').click()
        code = self.driver.find_element('xpath', '//*[contains(text(),"【华盟科技】验证码：")]').text[10:16]
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return code

    def input_code(self, type_, express):
        # code = self.get_code()
        code = self.obtain_code()
        el = self.locator(type_, express)
        el.send_keys(code)

    def action_move_slide(self, type_, express):
        try:
            el = self.locator(type_, express)
            ActionChains(self.driver).click_and_hold(el).move_by_offset(500, 0).release().perform()
        except Exception as e:
            logging.error(f"拖动滑块失败，原因：{e}")
            raise


    def js_find(self, type, express2):
        try:
            self.locator(type, express2)
            self.js_click(type, express2)
        except:
            logging.info("不需要点击")


    def check_seleted(self, type, express):
        r = self.locator(type, express)
        if r.is_selected():
            pass
        else:
            self.click(type, express)


    def check_attribute_click(self, type, express, value):
        try:
            r = self.locator(type, express)
            value_list = str(value).split(";")
            if value_list[1] == r.get_attribute(value_list[0]):
                logging.info("属性值校验正确")
            else:
                logging.info(f"属性值校验不正确，{value_list[1]}不等于{value_list[0]}")
                r.click()
        except Exception as e:
            logging.error(e)
            logging.error(f"属性值校验不正确{r.get_attribute(value_list[0])}不等于预设的{value_list[1]}")
            raise Exception(f"属性值校验不正确{r.get_attribute(value_list[0])}不等于预设的{value_list[1]}")


    def uploadfile(self,filePath):
        filePath = os.path.join(config.testdatas_dir, filePath)
        self.logger.info(f"文件名称是{filePath}")
        try:
            keyboard = Controller()
            pyperclip.copy(filePath)
            with keyboard.pressed(Key.ctrl):
                keyboard.press('v')
                keyboard.release('v')
                self.sleep(1)
            with keyboard.pressed(Key.alt):
                self.sleep(1)
                keyboard.press('o')
                keyboard.release('o')
            self.logger.info(f"文件{filePath}上传成功")
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(f"文件{filePath}上传不成功,原因是{e}")

    def uploadfile1(self, filePath, browser_type="Chrome"):
        if browser_type == "Chrome":
            title = u"打开"
        else:
            title = "文件上传"
        # 32770‐ComboBoxEx32 ‐ComboBox ‐Edit
        dialog = win32gui.FindWindow("#32770", title)  # 一级窗口 ‘打开窗口’
        # 二级
        ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)
        # 三级
        ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, "ComboBox", None)
        # 四级
        edit = win32gui.FindWindowEx(ComboBox, 0, "Edit", None)
        # 32770‐Button
        button = win32gui.FindWindowEx(dialog, 0, "Button", None)  # 四级
        # 往文件名编辑框中输入文件路径
        # 上传操作
        filePath = os.path.join(config_path.file_data_dir, filePath)
        time.sleep(1)
        win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, filePath)
        time.sleep(1)
        # 点击打开按钮
        win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)

    def action_double_input(self, type, express, value):
        el = self.locator(type, express)
        ActionChains(self.driver).double_click(el).send_keys(value).perform()

    def scroll_into_view(self, type, express):
        try:
            el = self.locator(type, express)
            js2 = "arguments[0].scrollIntoView(true);"
            self.driver.execute_script(js2, el)
        except:
            logging.error(f"操作元素{type, express},调整视图失败")
            logging.error(traceback.format_exc())
            # raise Exception(f"操作元素{type, express},调整视图失败")

    def scrollIntoView1(self, method):
        try:
            js = f"document.evaluate('{method}',document).iterateNext().scrollLeft=document.evaluate('{method}',document).iterateNext().scrollWidth"
            self.driver.execute_script(js)
        except:
            logging.error(f"操作元素{method},调整视图失败")
            logging.error(traceback.format_exc())
            raise Exception(f"操作元素{method},调整视图失败")


    def wait_click(self,type,expres):
        loc = (type,expres)
        WebDriverWait(self.driver, 10, 1).until(EC.visibility_of_element_located(loc))
        time.sleep(1)
        self.click(type,expres)


    # 验证某个元素文本内容
    def assertText(self, type, express, expect):
        time.sleep(1)
        el = self.locator(type, express)
        fact = el.text
        if str(fact) != str(expect):
            logging.error(traceback.format_exc())
            raise Exception(f"assertText:{fact}!={expect},断言失败")

    def count_el_handler(self, type, express1, express2):
        try:
            els = self.locators(type, express1)
            for i in range(len(els)):
                els = self.locators(type, express1)
                els[-1].click()
                time.sleep(1)
                self.click(type, express2)
                time.sleep(1)
        except:
            logging.info("不需要处理")

    def vi_select(self, type_, express, operator):
        exp = express + "," + operator.strip()
        self.click(type_, exp)

    def vi_locator(self, type, express):
        time.sleep(0.2)
        exp = express.split('>')
        values = exp[0].split(',')
        value1 = values[0].strip()
        text = values[1].strip() if len(values) > 1 else ""
        idx = int(values[2].strip()) if len(values) > 2 else -1
        # WebDriverWait(self.driver, 10, 1).until(EC.visibility_of_any_elements_located((type, value1)))
        ret = self.driver.find_elements(type, value1)
        # outer = list(filter(lambda x: text.strip() in x.get_attribute("outerHTML"), ret))
        outer = [x for x in ret if text.strip() in x.get_attribute("outerHTML")]
        el1 = outer[idx]
        if len(exp) > 1:
            vlaue2 = exp[1]
            el2 = el1.find_element(type, vlaue2)
            return el2
        else:
            return el1

