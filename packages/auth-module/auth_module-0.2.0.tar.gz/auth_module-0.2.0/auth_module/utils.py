import secrets
import hashlib
import jwt
import time
from argon2 import PasswordHasher

# 初始化 Argon2 哈希器（更安全的密码哈希）
ph = PasswordHasher()

def generate_salt():
    """
    生成安全的随机Salt。

    Returns:
        str: 16字节的十六进制字符串。
    """
    return secrets.token_hex(16)

def hash_password(password, salt=None):
    """
    使用Argon2对密码进行哈希。

    Args:
        password (str): 明文密码。
        salt (str, optional): 自定义Salt。如果未提供，生成随机Salt。

    Returns:
        tuple: (hashed_password, salt) 或 (hashed_password, None) 如果使用默认Salt。
    """
    if salt is None:
        salt = generate_salt()
    try:
        hashed = ph.hash(password + salt)
        return hashed, salt
    except Exception as e:
        raise ValueError(f"密码哈希失败: {str(e)}")

def verify_password(password, hashed_password, salt):
    """
    验证密码是否匹配。

    Args:
        password (str): 明文密码。
        hashed_password (str): 存储的哈希密码。
        salt (str): 对应的Salt。

    Returns:
        bool: 密码是否匹配。
    """
    try:
        return ph.verify(hashed_password, password + salt)
    except Exception:
        return False

def generate_jwt(user_id, secret, expires_in=86400):
    """
    生成JWT令牌。

    Args:
        user_id (int): 用户ID。
        secret (str): JWT密钥。
        expires_in (int): 有效期（秒），默认24小时。

    Returns:
        str: JWT令牌。
    """
    payload = {
        'user_id': user_id,
        'exp': time.time() + expires_in
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_jwt(token, secret):
    """
    验证JWT令牌。

    Args:
        token (str): JWT令牌。
        secret (str): JWT密钥。

    Returns:
        dict or None: 解码后的载荷，如果无效返回None。
    """
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None

def generate_verify_code(length=6):
    """
    生成随机验证码。

    Args:
        length (int): 验证码长度，默认6位。

    Returns:
        str: 随机数字字符串。
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))

if __name__ == "__main__":
    # 测试工具函数
    password = "testpassword"
    salt = generate_salt()
    hashed, used_salt = hash_password(password, salt)
    print(f"Salt: {used_salt}")
    print(f"Hashed password: {hashed}")
    is_valid = verify_password(password, hashed, used_salt)
    print(f"Password valid: {is_valid}")
    token = generate_jwt(1, "secret_key")
    print(f"JWT Token: {token}")
    decoded = verify_jwt(token, "secret_key")
    print(f"Decoded JWT: {decoded}")