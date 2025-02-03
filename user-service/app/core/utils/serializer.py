from cryptography.fernet import Fernet
import base64
import os
from typing import Any
import json

class DataSerializer:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)

    def serialize(self, data: Any) -> str:
        """Serialize and encrypt data"""
        json_data = json.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return base64.b64encode(encrypted_data).decode()

    def deserialize(self, encrypted_str: str) -> Any:
        """Decrypt and deserialize data"""
        encrypted_data = base64.b64decode(encrypted_str.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode()) 