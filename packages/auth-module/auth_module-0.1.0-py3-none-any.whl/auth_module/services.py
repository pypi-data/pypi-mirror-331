from .models import UserStorage, VerifyStorage
from .utils import hash_password, generate_jwt, generate_salt, verify_password, generate_verify_code
from datetime import datetime, timedelta

class UserService:
    """
    用户服务，处理认证相关的业务逻辑。
    """

    def __init__(self, user_storage: UserStorage, verify_storage: VerifyStorage, config):
        """
        初始化用户服务。

        Args:
            user_storage (UserStorage): 用户数据存储实现。
            verify_storage (VerifyStorage): 验证记录存储实现。
            config (dict): 配置信息。
        """
        self.user_storage = user_storage
        self.verify_storage = verify_storage
        self.config = config

    def register(self, username, password):
        """
        注册新用户。

        Args:
            username (str): 用户名。
            password (str): 明文密码。

        Returns:
            dict: 用户数据（包含 user_id）。

        Raises:
            ValueError: 用户已存在或其他错误。
        """
        user = self.user_storage.find_by_username(username)
        if user:
            raise ValueError("用户名已存在")

        salt = generate_salt()
        password_hash, _ = hash_password(password, salt)
        user_data = {
            'username': username,
            'password_hash': password_hash,
            'salt': salt,
            'status': 1,
            'create_time': datetime.now(),
        }
        saved_user = self.user_storage.save_user(user_data)
        if 'user_id' not in saved_user:
            raise ValueError("注册失败，用户ID缺失")
        print(f"注册返回的用户数据: {saved_user}")  # 添加调试打印
        return saved_user

    def login(self, username, password, ip):
        """
        用户登录。

        Args:
            username (str): 用户名。
            password (str): 明文密码。
            ip (str): 客户端IP地址。

        Returns:
            str: JWT令牌。

        Raises:
            ValueError: 用户名或密码错误。
        """
        user = self.user_storage.find_by_username(username)
        if not user:
            self.user_storage.log_login(None, 'password', ip, 0, "用户名或密码错误")
            raise ValueError("用户名或密码错误")

        if not verify_password(password, user['password_hash'], user['salt']):
            self.user_storage.log_login(user['user_id'], 'password', ip, 0, "用户名或密码错误")
            raise ValueError("用户名或密码错误")

        if 'user_id' not in user:
            raise ValueError("用户数据缺失user_id")

        token = generate_jwt(user['user_id'], self.config['jwt_secret'], self.config['jwt_expires'])
        self.user_storage.update_user(user['user_id'], {'last_login_time': datetime.now(), 'last_login_ip': ip})
        self.user_storage.log_login(user['user_id'], 'password', ip, 1)
        return token

    def send_verify_code(self, user_id, verify_type, content):
        """
        发送验证码（如短信或邮箱）。

        Args:
            user_id (int): 用户ID。
            verify_type (str): 验证类型（如'phone'或'email'）。
            content (str): 验证目标（如手机号或邮箱）。

        Returns:
            str: 生成的验证码。
        """
        code = generate_verify_code()
        expire_time = datetime.now() + timedelta(minutes=5)  # 验证码5分钟有效
        self.verify_storage.save_verify_code(user_id, verify_type, code, content, expire_time)
        # 这里假设有一个发送函数（需由使用者实现）
        print(f"Would send {verify_type} verify code {code} to {content}")
        return code

    def verify_code(self, content, code):
        """
        验证验证码。

        Args:
            content (str): 验证目标（如手机号或邮箱）。
            code (str): 用户输入的验证码。

        Returns:
            bool: 验证是否成功。
        """
        is_valid = self.verify_storage.check_verify_code(content, code)
        if is_valid:
            self.verify_storage.update_verify_status(content, code, 1)  # 标记为已使用
        else:
            self.verify_storage.update_verify_status(content, code, 2)  # 标记为过期
        return is_valid