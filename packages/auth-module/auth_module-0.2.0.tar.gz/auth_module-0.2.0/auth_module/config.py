import os
from dotenv import load_dotenv

def load_config(config_path=None):
    """
    加载认证模块的配置，从环境变量或配置文件读取。

    Args:
        config_path (str, optional): 配置文件路径（.env文件），默认使用当前目录的.env。

    Returns:
        dict: 配置字典。
    """
    # 加载环境变量（优先从config_path加载，如果没有则用默认.env）
    load_dotenv(config_path or '.env')

    return {
        'jwt_secret': os.getenv('JWT_SECRET', 'default_secret_123'),  # 默认密钥，开发时使用
        'jwt_expires': int(os.getenv('JWT_EXPIRES', 24 * 3600)),  # 默认24小时（以秒为单位）
        'auth_methods': os.getenv('AUTH_METHODS', 'email,phone,mfa').split(','),  # 支持的认证方式
        'db_config': {  # 数据库配置（由外部提供，模块不直接连接）
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'name': os.getenv('DB_NAME', 'auth_db'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
        },
        'sms_service': {  # 短信服务配置（第三方API）
            'provider': os.getenv('SMS_PROVIDER', 'twilio'),  # 例如Twilio或阿里云
            'api_key': os.getenv('SMS_API_KEY', ''),
            'api_secret': os.getenv('SMS_API_SECRET', ''),
        },
        'third_party': {  # 第三方登录配置
            'wechat': {
                'app_id': os.getenv('WECHAT_APP_ID', ''),
                'app_secret': os.getenv('WECHAT_APP_SECRET', ''),
            },
            'dingtalk': {
                'app_key': os.getenv('DINGTALK_APP_KEY', ''),
                'app_secret': os.getenv('DINGTALK_APP_SECRET', ''),
            },
        },
    }

if __name__ == "__main__":
    # 测试配置加载
    config = load_config()
    print(config)