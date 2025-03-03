from abc import ABC, abstractmethod

class UserStorage(ABC):
    """
    用户数据存储接口，定义认证模块需要的基本操作。
    使用者需实现这些方法，提供具体的数据库或存储实现。
    """

    @abstractmethod
    def find_by_email(self, email):
        """
        根据邮箱查找用户。

        Args:
            email (str): 用户邮箱。

        Returns:
            dict or None: 用户数据，如果不存在返回None。
        """
        pass

    @abstractmethod
    def save_user(self, user_data):
        """
        保存用户信息。

        Args:
            user_data (dict): 用户数据，如{'username': 'test', 'password_hash': 'hash', 'salt': 'salt'}.
        """
        pass

    @abstractmethod
    def update_user(self, user_id, updates):
        """
        更新用户信息。

        Args:
            user_id (int): 用户ID。
            updates (dict): 需要更新的字段，如{'last_login_time': datetime.now()}.
        """
        pass

    @abstractmethod
    def log_login(self, user_id, login_type, ip, status, fail_reason=None):
        """
        记录登录日志。

        Args:
            user_id (int or None): 用户ID（登录失败时可能为None）。
            login_type (str): 登录类型，如'password'或'thirdparty'。
            ip (str): 客户端IP地址。
            status (int): 登录状态（0:失败, 1:成功）。
            fail_reason (str, optional): 失败原因。
        """
        pass

class VerifyStorage(ABC):
    """
    验证记录存储接口，管理验证码等验证数据。
    """

    @abstractmethod
    def save_verify_code(self, user_id, verify_type, code, content, expire_time):
        """
        保存验证记录（如短信验证码、MFA码）。

        Args:
            user_id (int): 用户ID。
            verify_type (str): 验证类型，如'phone'、'email'或'mfa'。
            code (str): 验证码。
            content (str): 验证目标（如手机号或邮箱）。
            expire_time (datetime): 验证码过期时间。
        """
        pass

    @abstractmethod
    def check_verify_code(self, content, code):
        """
        验证验证码是否有效。

        Args:
            content (str): 验证目标（如手机号或邮箱）。
            code (str): 用户输入的验证码。

        Returns:
            bool: 验证是否成功。
        """
        pass

    @abstractmethod
    def update_verify_status(self, content, code, status):
        """
        更新验证记录状态（如已使用、过期）。

        Args:
            content (str): 验证目标。
            code (str): 验证码。
            status (int): 状态（0:未使用, 1:已使用, 2:过期）。
        """
        pass