# Auth Module

A reusable authentication module for Python applications, supporting multiple authentication methods (email, phone, MFA, etc.).

## Overview
This module provides a flexible and secure authentication system for Python projects. It supports user registration, login, multi-factor authentication (MFA), and verification via email, phone, or third-party services (e.g., WeChat, DingTalk). The module is designed to be modular, configurable, and reusable across different projects.

## Features
- User registration and login with password hashing (using Argon2).
- Multi-factor authentication (MFA) support.
- Verification via email, phone (SMS), or third-party login.
- JWT-based token authentication.
- Extensible storage interfaces for databases or other storage systems.
- Logging and auditing for security.

## Installation
To install the `auth_module`, use pip:

```bash
pip install auth_module
Alternatively, clone this repository and install locally:
bash
git clone https://github.com/drunksoul2021/auth_module.git
cd auth_module
pip install .
Requirements
Python 3.8 or higher
Dependencies: pyjwt==2.8.0, python-dotenv==1.0.0, argon2-cffi==23.1.0
Usage
Here’s a simple example to use the authentication module with a Flask application:
python
from flask import Flask, request, jsonify
from auth_module import init_auth

app = Flask(__name__)
auth = init_auth('.env')  # Load configuration from .env file

# Example storage implementation (using a mock for demonstration)
class MockStorage:
    def find_by_username(self, username):
        return {"user_id": 1, "username": username, "password_hash": "hashed", "salt": "salt"}
    def save_user(self, user_data): pass
    def update_user(self, user_id, updates): pass
    def log_login(self, user_id, login_type, ip, status, fail_reason=None): pass

# Set up storage
auth.set_storage(MockStorage())

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    result = auth.register(data['username'], data['password'])
    return jsonify(result)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    result = auth.login(data['username'], data['password'], request.remote_addr)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
Configuration
The module uses environment variables or a .env file for configuration. Create a .env file in the root directory with the following structure:
plaintext
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES=86400  # Token expiration in seconds (24 hours)
AUTH_METHODS=email,phone,mfa
DB_HOST=localhost
DB_PORT=3306
DB_NAME=auth_db
DB_USER=root
DB_PASSWORD=your_db_password
SMS_PROVIDER=twilio
SMS_API_KEY=your_sms_api_key
SMS_API_SECRET=your_sms_api_secret
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
DINGTALK_APP_KEY=your_dingtalk_app_key
DINGTALK_APP_SECRET=your_dingtalk_app_secret
An example .env.example is provided in the repository.
API Reference
The module exposes the following endpoints via the AuthController class:
POST /auth/register  
Payload: {"username": "string", "password": "string"}  
Response: {"code": int, "message": "string", "data": {"username": "string", "user_id": int}}
POST /auth/login  
Payload: {"username": "string", "password": "string"}  
Response: {"code": int, "message": "string", "data": {"token": "string"}}
POST /auth/send_verify_code  
Payload: {"user_id": int, "verify_type": "string", "content": "string"}  
Response: {"code": int, "message": "string", "data": {"code": "string"}}
POST /auth/verify_code  
Payload: {"content": "string", "code": "string"}  
Response: {"code": int, "message": "string", "data": null}
For more details, see the docs/ directory or the source code.
Testing
Run the tests using pytest:
bash
pytest tests/ -v
Contributing
Contributions are welcome! Please fork the repository, make changes, and submit a pull request. Ensure tests pass and add new tests if necessary.
License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements
Based on best practices from Python packaging and authentication standards.
Thanks to the open-source community for tools like pytest, pyjwt, and argon2-cffi.