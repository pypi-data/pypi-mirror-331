from .services import UserService
from .models import UserStorage, VerifyStorage

class AuthController:
    """
    认证控制器，处理HTTP请求并调用服务逻辑。
    """

    def __init__(self, config):
        """
        初始化控制器。

        Args:
            config (dict): 配置信息。
        """
        self.config = config
        self.user_service = None  # 延迟初始化，等待存储实现注入

    def set_storage(self, user_storage: UserStorage, verify_storage: VerifyStorage = None):
        """
        注入存储实现。

        Args:
            user_storage (UserStorage): 用户存储实现。
            verify_storage (VerifyStorage, optional): 验证记录存储实现。
        """
        self.user_service = UserService(user_storage, verify_storage, self.config)

    def register(self, username, password):
        """注册接口。"""
        if not self.user_service:
            return {'code': 500, 'message': '存储未初始化', 'data': None}
        try:
            user = self.user_service.register(username, password)
            # 打印调试信息，确认数据包含user_id
            print(f"DEBUG - user数据: {user}")
            print(f"DEBUG - user是否包含user_id: {'user_id' in user}")

            response = {
                'code': 200,
                'message': '注册成功',
                'data': {
                    'username': user['username'],
                    'user_id': user['user_id']  # 确保包含user_id
                }
            }
            # 打印返回的响应
            print(f"DEBUG - 返回的响应: {response}")
            return response
        except ValueError as e:
            return {'code': 400, 'message': str(e), 'data': None}

    def login(self, username, password, ip='127.0.0.1'):
        """
        登录接口。

        Returns:
            dict: 响应数据。
        """
        if not self.user_service:
            return {'code': 500, 'message': '存储未初始化', 'data': None}
        try:
            token = self.user_service.login(username, password, ip)
            return {'code': 200, 'message': '登录成功', 'data': {'token': token}}
        except ValueError as e:
            return {'code': 401, 'message': str(e), 'data': None}

    def send_verify_code(self, user_id, verify_type, content):
        """
        发送验证码接口。

        Returns:
            dict: 响应数据。
        """
        if not self.user_service:
            return {'code': 500, 'message': '存储未初始化', 'data': None}
        try:
            code = self.user_service.send_verify_code(user_id, verify_type, content)
            return {'code': 200, 'message': '验证码已发送', 'data': {'code': code}}
        except Exception as e:
            return {'code': 500, 'message': f'发送失败: {str(e)}', 'data': None}

    def verify_code(self, content, code):
        """
        验证验证码接口。

        Returns:
            dict: 响应数据。
        """
        if not self.user_service:
            return {'code': 500, 'message': '存储未初始化', 'data': None}
        is_valid = self.user_service.verify_code(content, code)
        if is_valid:
            return {'code': 200, 'message': '验证成功', 'data': None}
        return {'code': 400, 'message': '验证失败', 'data': None}