from .controllers import AuthController
from .config import load_config

def init_auth(config_path=None):
    """Initialize the authentication module."""
    config = load_config(config_path)
    return AuthController(config)

__version__ = "0.1.0"
__all__ = ['init_auth']  # 确保明确导出 init_auth