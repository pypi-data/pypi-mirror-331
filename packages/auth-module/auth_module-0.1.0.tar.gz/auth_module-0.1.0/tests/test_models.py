# tests/test_models.py
from auth_module.models import UserStorage, VerifyStorage
from abc import ABC

class MockUserStorage(UserStorage):
    def find_by_username(self, username):
        return {"user_id": 1, "username": username, "password_hash": "hash", "salt": "salt"} if username == "testuser" else None

    def save_user(self, user_data):
        print(f"Saving user: {user_data}")
        return user_data

    def update_user(self, user_id, updates):
        print(f"Updating user {user_id} with {updates}")

    def log_login(self, user_id, login_type, ip, status, fail_reason=None):
        print(f"Logging login: {user_id}, {login_type}, {ip}, {status}, {fail_reason}")

class MockVerifyStorage(VerifyStorage):
    def save_verify_code(self, user_id, verify_type, code, content, expire_time):
        print(f"Saving verify code: {user_id}, {verify_type}, {code}, {content}, {expire_time}")

    def check_verify_code(self, content, code):
        return content == "1234567890" and code == "1234"

    def update_verify_status(self, content, code, status):
        print(f"Updating verify status: {content}, {code}, {status}")

def test_user_storage():
    user_storage = MockUserStorage()
    user = user_storage.find_by_username("testuser")
    assert user == {"user_id": 1, "username": "testuser", "password_hash": "hash", "salt": "salt"}
    user_storage.save_user({"username": "testuser2", "password_hash": "hash2", "salt": "salt2"})
    user_storage.update_user(1, {"last_login_time": "2025-02-25"})
    user_storage.log_login(1, "password", "127.0.0.1", 1)

def test_verify_storage():
    verify_storage = MockVerifyStorage()
    verify_storage.save_verify_code(1, "phone", "1234", "1234567890", "2025-02-25 12:00:00")
    assert verify_storage.check_verify_code("1234567890", "1234") == True
    verify_storage.update_verify_status("1234567890", "1234", 1)