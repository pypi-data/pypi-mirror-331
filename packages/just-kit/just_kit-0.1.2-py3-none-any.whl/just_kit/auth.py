import os
import pickle
import subprocess
import logging
import requests
from bs4 import BeautifulSoup
from .utils import *
from typing import Optional

class Authenticator:
    '''
    用于登录信息门户的类
    '''
    def __init__(self, service: str = "http://my.just.edu.cn/", debug=False,auto_login=True):
        '''
        初始化函数
        :param service: 登录的服务,推荐使用默认值 http://my.just.edu.cn/
        :param debug: 是否开启调试模式
        :param auto_login: 是否自动读取保存的cookies以快速登录
        '''
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(level=logging.INFO)
        # 用于储存登入后的一些数据
        self.service = service
        self.login_data = {}
        self.session = requests.Session()
        self.cookie_file = ".cookies_" + \
            self.service.replace('http://', "").replace('/', '_') + ".pkl"  # 根据service生成唯一的cookie文件名
        self.headers = {
            "Host": "ids2.just.edu.cn",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        }
        self.ignore_cookies = ['Location']  # 要忽略的 cookie 名列表
        self.auto_login=auto_login
        if auto_login:
            self.load_cookies()  # 初始化时尝试加载cookie
            if not self.check():
                self.expire() # 自动登入失败

    def save_cookies(self):
        """保存cookies到文件"""
        filtered_cookies = {
            name: value for name,
            value in self.session.cookies.items() if name not in self.ignore_cookies}
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)
            
    def load_cookies(self):
        """
        从文件加载cookies
        会自动忽略location
        """
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                for name, value in cookies.items():
                    if name not in self.ignore_cookies:
                        self.session.cookies.set(name, value)

    def jsessionid(self)->Optional[str]:
        '''
        获取JSESSIONID,如果有JSESSIONID返回,否则返回None
        '''
        d = self.session.cookies
        return d["JSESSIONID"] if 'JSESSIONID' in d else None

    def encrypt_with_js(self, password) -> Optional[str]:

        """
        使用 js 脚本加密数据
        :param password: 要加密的密码
        :return: 加密后的数据
        """
        try:
            import execjs
            import os
            # 构建 js 文件的绝对路径
            js_path = os.path.join(
                os.path.dirname(__file__), "js", "security.js")
            # 读取加密脚本
            with open(js_path, "r", encoding="utf-8") as f:
                js_code = f.read()
            code = '''
            // 获取命令行参数
            function encrypt(data) {
                RSAUtils.setMaxDigits(131);
                var key = RSAUtils.getKeyPair("010001", '', "008aed7e057fe8f14c73550b0e6467b023616ddc8fa91846d2613cdb7f7621e3cada4cd5d812d627af6b87727ade4e26d26208b7326815941492b2204c3167ab2d53df1e3a2c9153bdb7c8c2e968df97a5e7e01cc410f92c4c2c2fba529b3ee988ebc1fca99ff5119e036d732c368acf8beba01aa2fdafa45b21e4de4928d0d403");
                return RSAUtils.encryptedString(key, data);
            }
            '''
            js_code += code
            # 创建一个JavaScript上下文
            ctx = execjs.compile(js_code)
            result = ctx.call("encrypt", password)
            return result
        except Exception as e:
            self.logger.error(f"Error executing JavaScript: {e}")
            return None
    
    def login(self, account: str, password: str):

        if self.check():
            return

        """
        接受账户和密码进行登录
        :param account: 账户
        :param password: 密码
        """
        with self.session as session:

            self.headers['HOST'] = get_host_from_url(self.service)
            # 直接访问service并得到跳转地址
            res = session.get(
                self.service,
                headers=self.headers,
                allow_redirects=False,
            )
            print( res.cookies.get_dict())
            # 该服务登入地址
            target = res.headers["Location"]
            # debug
            self.logger.debug(f"---第一次访问---")
            self.logger.debug(f"{res.status_code}->{target}")
            self.logger.debug(res.headers)
            self.logger.debug(session.cookies.get_dict())
            # 在跳转时要重置HOST和Origin防止404
            self.headers['HOST'] = get_host_from_url(target)
            self.headers["Origin"] = get_origin(target)

            res = session.get(
                abs_url(self.service,target),
                headers=self.headers,
                allow_redirects=False,
            )
            # debug
            self.logger.debug(f"{res.status_code}->{target}")
            self.logger.debug(res.headers)
            self.logger.debug(session.cookies.get_dict())
            # find execution
            soup = BeautifulSoup(res.text, "html.parser")
            execution_input = soup.find("input", {"name": "execution"})
            if execution_input:
                execution_value = execution_input.get("value")
            else:
                self.logger.error("未找到名为execution的input元素")
            # login data construct
            data = {
                "username": account,
                "password": self.encrypt_with_js(password),
                "_eventId": "submit",
                "submit": "登+录",
                "encrypted": "true",
                "loginType": "1",
                "execution": execution_value,
            }
            # login
            res = session.post(
                target,
                headers=self.headers,
                data=data,
                allow_redirects=False)
            if res.status_code == 302:
                self.logger.info("登入成功")
                self.save_cookies()
                target = res.headers["Location"]
                # debug
                self.logger.debug(f"{res.status_code}->{target}")
                self.logger.debug(session.cookies.get_dict())
                self.headers["Origin"] = get_origin(target)
                self.headers['HOST'] = get_host_from_url(target)
                # last
                res = session.get(
                    abs_url(self.service,target),
                    headers=self.headers,
                    allow_redirects=False)
                # debug
                self.logger.debug(res.status_code)
                self.logger.debug(session.cookies.get_dict())
                # 如果有跳转则输出跳转地址
                if res.status_code == 302:
                    target = res.headers["Location"]
                    self.logger.debug('->'+target)
            else:
                self.logger.error("登录失败")
                return -1
        return 0

    def expire(self):
        """
        强制清除Cookies信息过期
        """
        self.session.cookies.clear()
        # 删除cookie文件
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)

    def check(self) -> bool:
        """
        检查登录是否失效
        :return: 如果登录有效返回True,否则返回False
        """
        res = self.session.get(
            self.service,
            allow_redirects=False,
        )
        if res.status_code == 302:
            return False
        else:
            return True
