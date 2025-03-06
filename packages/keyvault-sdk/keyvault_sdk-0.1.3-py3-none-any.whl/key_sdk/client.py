from key_sdk.rsa import RSAClient
from key_sdk.secret import KeyRequest
from key_sdk.aes import AESClient
from apscheduler.schedulers.background import BackgroundScheduler


class BaseKeyClient(object):
    def __init__(
            self,
            **kwargs
    ):
        # 密钥请求
        self.key_request = KeyRequest(**kwargs)
        # 初始化密钥信息
        self.init_key()
        # 定时更新密钥
        self.scheduler = BackgroundScheduler()
        self.crontab()

    def crontab(self):
        # 添加任务，设置为每天0点执行
        self.scheduler.add_job(self.init_key, 'cron', hour=0, minute=0)
        self.scheduler.start()

    def init_key(self):
        pass

    def encrypt(self, plaintext):
        pass

    def decrypt(self, ciphertext):
        pass


class AESKeyClient(BaseKeyClient):
    def __init__(
            self,
            **kwargs
    ):
        """
        host: str, 密钥管理服务地址
        app_name: str, 应用名
        app_secret: str, 应用密钥
        aes_key_sid: str, AES密钥别名SID
        """
        self.aes_client = None
        self.aes_key_version_list = []
        self.aes_latest_key_version = None
        self.aes_keys = {}
        self.default_iv = None
        super().__init__(**kwargs)

    def init_key(self):
        # 获取aes密钥版本列表
        self.aes_key_version_list = self.key_request.get_aes_key_version()
        # 获取最新的密钥版本
        self.aes_latest_key_version = self.aes_key_version_list[-1]
        # 更新密钥信息
        self.init_aes_keys()
        # AES加解密实例
        self.aes_client = AESClient(self.aes_keys, self.aes_latest_key_version,
                                    default_iv=self.default_iv)

    def init_aes_keys(self):
        for version in self.aes_key_version_list:
            if version in self.aes_keys:
                continue
            self.aes_keys[version] = self.key_request.get_aes_key(version)

    def encrypt(self, plaintext):
        # AES加密
        return self.aes_client.encrypt(plaintext)

    def decrypt(self, ciphertext, **kwargs):
        # AES解密
        return self.aes_client.decrypt(ciphertext, **kwargs)


class RSAKeyClient(BaseKeyClient):
    def __init__(
            self,
            **kwargs
    ):
        """
        host: str, 密钥管理服务地址
        app_name: str, 应用名
        app_secret: str, 应用密钥
        rsa_private_key_sid: str, RSA私钥别名SID
        """
        self.rsa_client = None
        self.rsa_private_key = None
        super().__init__(**kwargs)
        self.init()

    def init(self):
        # rsa私钥
        self.rsa_private_key = self.key_request.get_rsa_key()
        # RSA加解密实例
        self.rsa_client = RSAClient(self.rsa_private_key)

    def encrypt(self, plaintext):
        # RSA加密
        return self.rsa_client.encrypt(plaintext)

    def decrypt(self, ciphertext):
        # RSA解密
        return self.rsa_client.decrypt(ciphertext)


if __name__ == '__main__':
    # AES测试示例
    kwargs = {
        'host': 'http://127.0.0.1:9094',
        'app_name': 'test',
        'app_secret': '1111111111111',
        'aes_key_sid': 'sid-xxxxxxxxxxxxxxx',
    }
    # 要加密的明文
    plaintext = b'\x80\xbd\x81=\xb9\xcf(\xc0eI\xe8\x1de\xf4\xc2\x1b\\|gVh\xe73\xa4\r\x97\xb2\xe1f\x90(\x88'
    aes_key_client = AESKeyClient(**kwargs)
    ciphertext_base64 = aes_key_client.encrypt(plaintext)
    print("Ciphertext (Base64):", ciphertext_base64)
    # 解密时须传入必要字段
    kwargs = {
        "ad_account": "san.zhang",
        "ciphertext_class": "CustomerInfo",
        "ciphertext_hash": "d17f25ecfbcc7857f7bebea469308be0b2580943e96d13a3ad98a13675c4bfc2",
        "ciphertext_type": "手机号",
        "system_name": "finder",
        "username": "张三"
    }
    decrypted_text = aes_key_client.decrypt(ciphertext_base64, **kwargs)
    print("Decrypted Text:", decrypted_text)
