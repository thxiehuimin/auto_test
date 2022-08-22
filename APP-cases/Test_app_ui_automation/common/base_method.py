# coding=utf-8
import uiautomator2 as u2
import logging
import time
from appium import webdriver as app_web_driver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import config_path
import os
from email.parser import Parser
import poplib
import base64
import re


class BasePageMethod(object):

    def __init__(self):
        self.driver = None

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

    def open_app(self, devices, package):
        try:
            for i in range(6):
                logging.info("正在创建驱动对象")
                self.d = u2.connect_usb(devices)
                logging.info("正在打开app")
                self.d.app_start(package)
                self.wait(1)
                self.d(text='同意并接受').click()
                self.wait(10)
                if self.d.xpath('//*[@content-desc="欢迎使用华盟·税纪云"]').exists:
                    logging.info("进入登录页成功")
                    break
                else:
                    self.d.app_stop(package)
                    self.d.app_clear(package)

                if i == 5:
                    raise '打开app失败'
        except Exception as e:
            logging.error(f"无法打开app,异常原因：{e}")
            raise

    def app_implicitly_wait(self, s):
        try:
            self.d.implicitly_wait(s)
            logging.info(f"设置隐式等待{s}秒")
        except Exception as e:
            logging.error(f"设置隐式等待失败,异常原因：{e}")
            raise

    def app_locator(self, type_, express):
        try:
            if type_ == 'xpath':
                element = self.d.xpath(express)
                logging.info('通过xpath定位元素{}，成功!'.format(express))
                return element
            elif type_ == 'description':
                element = self.d(description=express)
                logging.info('通过description定位元素{}，成功!'.format(express))
                return element
            elif type_ == 'text':
                element = self.d(text=express)
                logging.info('通过text定位元素{}，成功!'.format(express))
                return element
            else:
                logging.info('该定位方式暂不支持')
                return None

        except Exception as e:
            logging.error(f"定位元素{express}失败，原因:{e}")
            raise

    def click_key(self, key):
        try:
            self.d.press(key)
            logging.info(f"按下{key}键")
        except Exception as e:
            logging.error(f"按下{key}键失败,原因：{e}")
            raise

    def app_click(self, type_, express):
        try:
            if type_ == 'coordinate':
                coo = express[1:-1].split(',')
                self.d.click(float(coo[0]), float(coo[1]))
                logging.info(f"点击坐标({coo[0]},{coo[1]})")
            else:
                try:
                    self.app_locator(type_, express).click()
                    logging.info(f"点击元素{express}")
                except Exception as e:
                    logging.info(f"点击元素{express}失败，错误原因{e}，2秒后正在重试")
                    self.wait(2)
                    self.app_locator(type_, express).click()
                    logging.info(f"点击元素{express}")
        except Exception as e:
            logging.error(f"点击元素{express}失败,原因：{e}")
            raise

    def app_get_code(self, type_, express):
        try:
            for i in range(3):
                self.app_locator(type_, express).click()
                logging.info(f"点击元素{express}")
                self.wait(1)
                if self.d(text="验证码发送成功").exists:
                    logging.info(f"验证码发送成功")
                    break
                else:
                    self.d.press('back')
                if i == 2:
                    logging.info(f"验证码发送失败")
                    raise
        except Exception as e:
            logging.error(f"点击获取验证码失败,原因：{e}")
            raise

    def app_input(self, type_, express, value):  # 输入
        try:
            self.d.xpath(express).set_text(str(value))
            logging.info(f"在元素{express}中输入:{value}")
        except Exception as e:
            logging.error(f"在元素{express}中输入{value}失败,原因：{e}")
            raise

    def implicitly_wait(self, s):  # 设置隐式等待
        try:
            self.driver.implicitly_wait(s)
            logging.info(f"设置隐式等待{s}秒")
        except Exception as e:
            logging.error(f"设置隐式等待失败,异常原因：{e}")
            raise

    @staticmethod
    def wait(s):  # 等待
        logging.info(f"等待{s}秒")
        time.sleep(s)

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
            if type_[0] == '$':
                element = WebDriverWait(self.driver, 10, 0.5).until(
                    lambda el: self.driver.find_element(type_[1:], express), message='TimeoutException')
                logging.info('使用显示等待定位元素{}，成功!'.format((type_[1:], express)))
                return element
            else:
                element = self.driver.find_element(type_, express)
                logging.info('定位元素{}，成功!'.format((type_[1:], express)))
                return element

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
            raise

    def app_wait_ele_visible(self, txt):  # 等待元素可见
        logging.info(f'正在校验中...')
        for j in range(6):
            if self.d(text=txt).exists:
                logging.error(f"校验不通过")
                raise
            self.wait(0.5)
        logging.info(f'校验通过')

    def input(self, type_, express, value):  # 输入
        try:
            self.locator(type_, express).send_keys(value)
            logging.info(f"在元素{type_, express}中输入:{value}")
        except Exception as e:
            logging.error(f"在元素{type_, express}中输入{value}失败,原因：{e}")
            raise

    def action_input(self, type_, express, value):
        el = self.locator(type_, express)
        ActionChains(self.driver).click(el).pause(1).send_keys(value).perform()

    def delete_input(self, type_, express, value):  # 清空后输入
        try:
            el = self.locator(type_, express)
            el.send_keys(u'\ue009', 'a')
            el.send_keys(u'\ue017')
            logging.info(f"清除元素{type_, express}中的内容")
            el.send_keys(value)
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
                logging.info(f"点击元素{type_, express}")
            except Exception as e:
                logging.info(f"点击元素{type_, express}失败，错误原因{e}，2秒后正在重试")
                self.wait(2)
                self.locator(type_, express).click()
                logging.info(f"点击元素{type_, express}")
        except Exception as e:
            logging.error(f"点击元素{type_, express}失败,原因：{e}")
            raise

    def js_click(self, type_, express):  # 使用js点击
        try:
            try:
                self.driver.execute_script("arguments[0].click()", self.locator(type_, express))
                logging.info(f"点击元素{type_, express}")
            except Exception as e:
                logging.info(f"js点击元素{type_, express}失败，错误原因{e}，2秒后正在重试")
                self.wait(2)
                self.driver.execute_script("arguments[0].click()", self.locator(type_, express))
                logging.info(f"点击元素{type_, express}")
        except Exception as e:
            logging.error(f"使用js点击元素{type_, express}失败,原因：{e}")
            raise

    def save_screenshot(self, screen_path):  # 保存截图
        self.driver.save_screenshot(screen_path)
        logging.info(f"保存错误截图成功，截图所在路径：{screen_path}")

    def scroll_into_view(self, type_, express):  # 调整视图
        try:
            el = self.locator(type_, express)
            js_str = "arguments[0].scrollIntoView(true);"
            self.driver.execute_script(js_str, el)
            logging.info(f"调整视图至元素{type_, express}")
        except Exception as e:
            logging.error(f"调整视图至元素{type_, express}失败,原因：{e}")
            raise

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
                logging.info('定位元素{}，成功!'.format((type_[1:], express)))
                return elements

        except Exception as e:
            logging.error(f"定位元素{type_, express}失败，原因:{e}")
            raise

    def check_list_value(self, type_, express, value):  # 校验表中元素
        els = self.locators(type_, express)
        page_data = []
        for i in els:
            num_str = i.text.replace(',', '').replace('-', '', 1).replace('%', '')
            if num_str[:num_str.find('.')].isnumeric() and num_str[num_str.find('.') + 1:].isnumeric():
                page_data.append(i.text)

        if str(page_data) == value:  # 对比预期结果和实际结果
            logging.info("数据校验正确")
        else:
            logging.error(f"数据校验不正确，页面中的数据:{page_data}不等于预设的数据：{value}")
            raise

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

    def login_prd(self, parameter):
        account, password, express1, express2, express3, express4, express5, express6, express7 = parameter.split(',')
        for i in range(10):
            self.input('xpath', express1, account)  # 输入用户名
            self.input('xpath', express2, password)  # 输入密码
            self.action_move_slide('xpath', express3)  # 拖动滑块
            self.click('xpath', express4)  # 点击获取验证码
            self.wait(30)
            try:
                if i == 0:
                    self.driver.execute_script("window.open('http://10.99.1.127/','_blank');")

                    # 切换到指定句柄的窗口
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.find_element('xpath', '//input[@id="f_user"]').send_keys('adam.zhang')
                    self.driver.find_element('xpath', '//input[@id="f_pass"]').send_keys('jie@1113')
                    self.driver.find_element('xpath', '//div[contains(text(),"登录")]').click()
                    self.driver.find_element('xpath', '//*[@id="menuitem_msglist_inbox"]').click()
                    code = self.driver.find_element('xpath', '(//*[contains(text(),"【华盟科技】验证码：")])[1]').text[10:16]
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.input('xpath', express5, code)
                else:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.refresh()
                    code = self.driver.find_element('xpath', '(//*[contains(text(),"【华盟科技】验证码：")])[1]').text[10:16]
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    self.input('xpath', express5, code)

                self.click('xpath', express6)  # 点击阅读协议
                self.click('xpath', express7)  # 点击登录
            except:
                logging.info('邮箱异常，正在重试')
            try:
                WebDriverWait(self.driver, 30, 0.5).until(
                    lambda el: self.driver.find_element('xpath', '//*[contains(text(),"成功")]'),
                    message='TimeoutException')
                break
            except:
                logging.error('获取验证码错误，即将开始重试,已重试:{}次'.format(i))
                self.refresh()

    def login_mobile_prd(self, express1, express2, express3):
        logging.info('通过无头模式创建Chrome浏览器驱动')
        options = Options()
        options.add_argument('--headless')  # 设置无头模式
        options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        options.add_argument("--disable-blink-features=AutomationControlled")  # 浏览器环境补齐
        web_driver = getattr(webdriver, 'Chrome')(options=options)
        logging.info(f"使用无头模式打开Chrome浏览器")
        web_driver.set_window_size(1920, 1500)
        logging.info('将浏览器窗口设置为1920*1500')
        flag = False
        for i in range(10):
            try:
                if i == 0:
                    self.wait(54)
                    logging.info('打开网址:http://10.99.1.127/')
                    web_driver.get('http://10.99.1.127/')
                    self.wait(2)
                    logging.info('输入账号：adam.zhang')
                    web_driver.find_element('xpath', '//input[@id="f_user"]').send_keys('adam.zhang')
                    logging.info('输入密码：jie@1113')
                    web_driver.find_element('xpath', '//input[@id="f_pass"]').send_keys('jie@1113')
                    logging.info('点击登录')
                    web_driver.find_element('xpath', '//div[contains(text(),"登录")]').click()
                    self.wait(2)
                    logging.info('收件箱')
                    web_driver.find_element('xpath', '//*[@id="menuitem_msglist_inbox"]').click()
                    self.wait(2)
                    logging.info('正在查找验证码')
                    code = web_driver.find_element('xpath', '(//*[contains(text(),"【华盟科技】验证码：")])[1]').text[10:16]
                    logging.info(f'输入验证码{code}')
                    self.app_locator('xpath', express2).set_text(code)  # 输入验证码
                else:
                    logging.info('点击获取验证码')
                    self.d.xpath(express1).click()  # 点击获取验证码
                    self.wait(60)
                    logging.info('刷新页面')
                    web_driver.refresh()
                    logging.info('正在查找验证码')
                    code = web_driver.find_element('xpath', '(//*[contains(text(),"【华盟科技】验证码：")])[1]').text[10:16]
                    logging.info(f'输入验证码{code}')
                    self.app_locator('xpath', express2).set_text(code)  # 输入验证码
                logging.info('点击登录')
                self.d.xpath(express3).click()  # 点击登录
                logging.info(f'判断是否登录成功')

                for j in range(30):
                    if self.d(text="登录成功").exists:
                        logging.info(f'登录成功')
                        flag = True
                        break
                    else:
                        self.wait(0.5)
                if flag:
                    break
                else:
                    logging.info(f'验证码错误，即将开始重试,已重试{i}次')
            except Exception as e:
                logging.info(f'邮箱异常，正在重试，异常原因{e}')
        if flag is False:
            logging.error('登录失败')
            raise

    def action_move_slide(self, type_, express):
        try:
            el = self.locator(type_, express)
            ActionChains(self.driver).click_and_hold(el).move_by_offset(500, 0).release().perform()
        except Exception as e:
            logging.error(f"拖动滑块失败，原因：{e}")
            raise

    def try_click(self, type_, express):  # 尝试点击，点不到则不点
        try:
            self.locator(type_, express).click()
            logging.info(f"点击元素{type_, express}")
        except Exception as e:
            logging.error(f"不点击元素{type_, express},{e}")

    def find_refresh(self, type_, express):
        for i in range(10):
            try:
                self.wait_ele_visible(type_, express)
                break
            except:
                logging.info('页面空白，即将刷新，已刷新{}次')
                self.refresh()

    def try_js_click(self, type_, express):  # 尝试点击，点不到则不点
        try:
            self.driver.execute_script("arguments[0].click()", self.locator(type_, express))
            logging.info(f"点击元素{type_, express}")
        except Exception as e:
            logging.error(f"不点击元素{type_, express},{e}")

    def close_all(self):
        self.driver.close()
        self.driver.quit()
        logging.info('关闭浏览器')
