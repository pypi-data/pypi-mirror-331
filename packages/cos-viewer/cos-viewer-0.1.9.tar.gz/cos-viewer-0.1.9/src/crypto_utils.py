import os
import base64
import hashlib
from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = Path.home() / ".cos-viewer" / ".key"

class CryptoUtils:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _get_or_create_key(self):
        if KEY_FILE.exists():
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        
        # 基于设备信息生成密钥
        device_info = self._get_device_info()
        key = base64.urlsafe_b64encode(hashlib.sha256(device_info.encode()).digest())
        
        # 保存密钥
        KEY_FILE.parent.mkdir(exist_ok=True)
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        
        return key
    
    def _get_device_info(self):
        # 获取设备特征信息，用于生成唯一的加密密钥
        info = []
        info.append(str(os.getuid()))
        info.append(str(os.geteuid()))
        info.append(str(Path.home()))
        return ':'.join(info)
    
    def encrypt(self, data: str) -> str:
        if not data:
            return data
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return encrypted_data
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            raise ValueError("Invalid encrypted data")
